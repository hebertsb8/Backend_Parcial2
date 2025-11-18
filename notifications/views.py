# notifications/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from typing import Any, Dict, cast

from .models import DeviceToken, Notification, NotificationPreference, NotificationCampaign
from .serializers import (
    DeviceTokenSerializer,
    DeviceTokenCreateSerializer,
    NotificationSerializer,
    NotificationListSerializer,
    SendNotificationSerializer,
    NotificationPreferenceSerializer,
    NotificationStatsSerializer,
    NotificationCampaignSerializer,
    NotificationCampaignListSerializer,
)
from .notification_service import NotificationService
from api.permissions import IsAdminUser


class DeviceTokenViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar tokens de dispositivos.

    Los usuarios solo pueden ver y gestionar sus propios tokens.
    """

    serializer_class = DeviceTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar tokens por usuario actual"""
        return DeviceToken.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def register(self, request):
        """Registra un nuevo token de dispositivo para el usuario actual."""
        serializer = DeviceTokenCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(Dict[str, Any], serializer.validated_data)

        try:
            device_token = NotificationService.register_device_token(
                user=request.user,
                token=validated_data["token"],
                platform=validated_data.get("platform", DeviceToken.Platform.WEB),
                device_name=validated_data.get("device_name"),
                validate_token=True  # Validar token por defecto
            )

            return Response(DeviceTokenSerializer(device_token).data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({
                "error": "Token FCM inválido",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error registrando token de dispositivo: {e}")
            return Response({
                "error": "Error interno del servidor"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["post"])
    def unregister(self, request):
        """Desregistra (desactiva) un token de dispositivo."""

        token = request.data.get("token")
        if not token:
            return Response({"error": "Token es requerido"}, status=status.HTTP_400_BAD_REQUEST)

        success = NotificationService.unregister_device_token(token)

        if success:
            return Response({"message": "Token desactivado correctamente"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Token no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def firebase_config(self, request):
        """Proporciona configuración segura de Firebase para el frontend.

        Solo expone la configuración necesaria para obtener tokens FCM,
        manteniendo las credenciales sensibles en el backend.
        """
        from django.conf import settings

        # Configuración limitada que se puede exponer al frontend
        config = {
            'apiKey': getattr(settings, 'FIREBASE_PUBLIC_API_KEY', None),
            'authDomain': getattr(settings, 'FIREBASE_AUTH_DOMAIN', None),
            'projectId': getattr(settings, 'FIREBASE_PROJECT_ID', None),
            'storageBucket': getattr(settings, 'FIREBASE_STORAGE_BUCKET', None),
            'messagingSenderId': getattr(settings, 'FIREBASE_MESSAGING_SENDER_ID', None),
            'appId': getattr(settings, 'FIREBASE_APP_ID', None),
        }

        # Verificar que tengamos la configuración necesaria
        required_fields = ['apiKey', 'authDomain', 'projectId', 'messagingSenderId', 'appId']
        missing_fields = [field for field in required_fields if not config.get(field)]

        if missing_fields:
            return Response({
                'error': f'Configuración de Firebase incompleta. Faltan: {", ".join(missing_fields)}'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({
            'success': True,
            'config': config,
            'vapidKey': getattr(settings, 'FIREBASE_VAPID_KEY', None)  # Para notificaciones web push
        })


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para ver notificaciones y endpoints admin de envío."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return NotificationListSerializer
        if self.action == "send":
            return SendNotificationSerializer
        return NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def unread(self, request):
        notifications = self.get_queryset().filter(
            status__in=[Notification.Status.PENDING, Notification.Status.SENT]
        )
        serializer = NotificationListSerializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = NotificationService.get_unread_count(request.user)
        return Response({"count": count})

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        """Marca una notificación como leída."""

        if pk is None:
            return Response({"error": "ID de notificación requerido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            notification_id = int(pk)
        except (TypeError, ValueError):
            return Response({"error": "ID de notificación inválido"}, status=status.HTTP_400_BAD_REQUEST)

        success = NotificationService.mark_notification_as_read(notification_id, request.user)

        if success:
            return Response({"message": "Notificación marcada como leída"}, status=status.HTTP_200_OK)
        return Response({"error": "Notificación no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        count = NotificationService.mark_all_as_read(request.user)
        return Response({"message": f"{count} notificaciones marcadas como leídas", "count": count})

    @action(detail=False, methods=["post"], permission_classes=[IsAdminUser])
    def send(self, request):
        """Envía notificaciones: admite user_ids, topic o device_tokens."""

        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(Dict[str, Any], serializer.validated_data)

        # prioridad: topic > device_tokens > user_ids > admins
        topic = validated_data.get("topic")
        device_tokens = validated_data.get("device_tokens")
        user_ids = validated_data.get("user_ids")

        # asegurarnos de que title y body estén presentes (serializer ya los valida)
        title = validated_data.get("title")
        body = validated_data.get("body")
        if title is None or body is None:
            return Response({"error": "title y body son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        if topic:
            result = NotificationService.send_notification_to_topic(
                topic=topic,
                title=title,
                body=body,
                notification_type=validated_data.get("notification_type", "SYSTEM"),
                data=validated_data.get("data"),
            )
        elif device_tokens:
            result = NotificationService.send_to_device_tokens(
                tokens=device_tokens,
                title=title,
                body=body,
                notification_type=validated_data.get("notification_type", "CUSTOM"),
                data=validated_data.get("data"),
                image_url=validated_data.get("image_url"),
            )
        elif user_ids:
            users = User.objects.filter(id__in=user_ids, is_active=True)
            result = NotificationService.send_notification_to_users(
                users=list(users),
                title=title,
                body=body,
                notification_type=validated_data.get("notification_type", "CUSTOM"),
                data=validated_data.get("data"),
                image_url=validated_data.get("image_url"),
            )
        else:
            result = NotificationService.send_to_all_admins(
                title=title,
                body=body,
                notification_type=validated_data.get("notification_type", "SYSTEM"),
                data=validated_data.get("data"),
            )

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def fcm_users(self, request):
        """Devuelve lista de usuarios con tokens FCM activos para envío de notificaciones."""

        # Obtener usuarios con tokens activos
        users_with_tokens = User.objects.filter(
            device_tokens__is_active=True
        ).distinct().select_related('profile')

        # Serializar la información necesaria
        users_data = []
        for user in users_with_tokens:
            # Obtener tokens activos del usuario
            active_tokens = DeviceToken.objects.filter(
                user=user,
                is_active=True
            ).values('platform', 'device_name', 'created_at')

            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'fcm_tokens': list(active_tokens),
                'tokens_count': len(active_tokens)
            }

            # Agregar información del perfil si existe
            if hasattr(user, 'profile'):
                user_data['role'] = user.profile.role
                user_data['full_name'] = f"{user.first_name} {user.last_name}".strip() or user.username

            users_data.append(user_data)

        return Response({
            'count': len(users_data),
            'users': users_data
        })

    @action(detail=False, methods=["get"])
    def stats(self, request):
        queryset = self.get_queryset()

        stats = {
            "total_notifications": queryset.count(),
            "unread_count": queryset.filter(status__in=[Notification.Status.PENDING, Notification.Status.SENT]).count(),
            "sent_count": queryset.filter(status=Notification.Status.SENT).count(),
            "failed_count": queryset.filter(status=Notification.Status.FAILED).count(),
            "by_type": dict(queryset.values("notification_type").annotate(count=Count("id")).values_list("notification_type", "count")),
            "recent_notifications": queryset[:10],
        }

        serializer = NotificationStatsSerializer(stats)
        return Response(serializer.data)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar preferencias de notificaciones."""

    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def my_preferences(self, request):
        preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"])
    def update_preferences(self, request):
        preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(preferences, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class NotificationCampaignViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar campañas de notificaciones.
    
    Solo administradores pueden crear y gestionar campañas.
    """
    serializer_class = NotificationCampaignSerializer
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NotificationCampaignListSerializer
        return NotificationCampaignSerializer
    
    def get_queryset(self):
        return NotificationCampaign.objects.all().order_by('-created_at')
    
    @action(detail=True, methods=["post"])
    def send_campaign(self, request, pk=None):
        """Envía la campaña a todos los usuarios con tokens FCM activos."""
        campaign = self.get_object()
        
        # Obtener usuarios con tokens activos
        users_with_tokens = User.objects.filter(
            device_tokens__is_active=True
        ).distinct()
        
        if not users_with_tokens.exists():
            return Response(
                {"error": "No hay usuarios con tokens FCM activos"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Enviar notificaciones usando el servicio
        result = NotificationService.send_notification_to_users(
            users=list(users_with_tokens),
            title=campaign.title,
            body=campaign.description or "Notificación de campaña",
            notification_type='CUSTOM',
            campaign_title=campaign.title,
            campaign_description=campaign.description,
            created_by=request.user
        )
        
        # Actualizar campaña con estadísticas
        campaign.total_users = result['total_users']
        campaign.successful_sends = result['successful_sends']
        campaign.failed_sends = result['failed_sends']
        campaign.is_completed = True
        campaign.save()
        
        return Response({
            "message": f"Campaña enviada a {result['total_users']} usuarios",
            "statistics": result
        })
    
    @action(detail=True, methods=["get"])
    def failed_notifications(self, request, pk=None):
        """Obtiene las notificaciones fallidas de la campaña."""
        campaign = self.get_object()
        failed_notifications = campaign.notifications.filter(status=Notification.Status.FAILED)
        
        serializer = NotificationListSerializer(failed_notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def campaign_stats(self, request, pk=None):
        """Obtiene estadísticas detalladas de la campaña."""
        campaign = self.get_object()
        
        stats = {
            "total_notifications": campaign.notifications.count(),
            "sent_notifications": campaign.notifications.filter(status=Notification.Status.SENT).count(),
            "failed_notifications": campaign.notifications.filter(status=Notification.Status.FAILED).count(),
            "pending_notifications": campaign.notifications.filter(status=Notification.Status.PENDING).count(),
            "read_notifications": campaign.notifications.filter(status=Notification.Status.READ).count(),
        }
        
        return Response(stats)


# Vista independiente para configuración de Firebase (pública)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def firebase_config_view(request):
    """Vista pública para proporcionar configuración de Firebase al frontend.

    Este endpoint es público porque el frontend necesita la configuración
    antes de que el usuario se autentique para obtener tokens FCM.
    """
    from django.conf import settings

    # Configuración limitada que se puede exponer al frontend
    config = {
        'apiKey': getattr(settings, 'FIREBASE_PUBLIC_API_KEY', None),
        'authDomain': getattr(settings, 'FIREBASE_AUTH_DOMAIN', None),
        'projectId': getattr(settings, 'FIREBASE_PROJECT_ID', None),
        'storageBucket': getattr(settings, 'FIREBASE_STORAGE_BUCKET', None),
        'messagingSenderId': getattr(settings, 'FIREBASE_MESSAGING_SENDER_ID', None),
        'appId': getattr(settings, 'FIREBASE_APP_ID', None),
    }

    # Verificar que tengamos la configuración necesaria
    required_fields = ['apiKey', 'authDomain', 'projectId', 'messagingSenderId', 'appId']
    missing_fields = [field for field in required_fields if not config.get(field)]

    if missing_fields:
        return Response({
            'error': f'Configuración de Firebase incompleta. Faltan: {", ".join(missing_fields)}'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(config)
