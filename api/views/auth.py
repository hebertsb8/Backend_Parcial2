# api/views/auth.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from ..serializers import UserSerializer, RegisterSerializer, UserProfileUpdateSerializer
from rest_framework import generics
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from ..serializers import PasswordResetRequestSerializer, SetNewPasswordSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Vista de registro"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# segundoparcial-backend/api/views/auth.py

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Vista de login mejorada (acepta username o email)"""
    # Aquí definimos la variable 'identifier'
    identifier = request.data.get('username')
    password = request.data.get('password')

    if not identifier or not password:
        return Response(
            {'error': 'Por favor proporciona un usuario/email y contraseña'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # La usamos aquí
    user = authenticate(username=identifier, password=password)

    if user is None:
        try:
            # Y la usamos aquí también
            user_by_email = User.objects.get(email=identifier)
            user = authenticate(username=user_by_email.username, password=password)
        except User.DoesNotExist:
            user = None

    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username': user.username
        })

    return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass # El usuario ya no tiene token, no hay nada que hacer
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Devuelve los datos del perfil del usuario logueado."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        """Actualiza el perfil del usuario logueado."""
        user = request.user
        # Usamos el nuevo serializador para validar y guardar los datos
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            # Devolvemos el perfil completo y actualizado
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """Cambia la contraseña del usuario logueado."""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # Validaciones
        if not old_password or not new_password or not confirm_password:
            return Response({
                'error': 'Todos los campos son requeridos: old_password, new_password, confirm_password'
            }, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({
                'error': 'La nueva contraseña y la confirmación no coinciden'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({
                'error': 'La nueva contraseña debe tener al menos 8 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que la contraseña actual sea correcta
        if not user.check_password(old_password):
            return Response({
                'error': 'La contraseña actual es incorrecta'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Cambiar la contraseña
        user.set_password(new_password)
        user.save()

        # Invalidar el token actual para forzar re-login
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass

        return Response({
            'message': 'Contraseña cambiada exitosamente. Por favor, inicia sesión nuevamente.'
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(generics.GenericAPIView):
    """
    Vista para solicitar el reseteo de contraseña.
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # No revelamos si el usuario no existe por seguridad
            return Response({'detail': 'If an account with this email exists, a password reset link has been sent.'},
                            status=status.HTTP_200_OK)

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        # El frontend recibirá este link (en un email en producción)
        # Por ahora, se imprimirá en la consola del backend.
        # TU_DOMINIO_FRONTEND debe ser reemplazado por la URL de tu app React
        reset_link = f"http://localhost:3000/reset-password/{uidb64}/{token}/"

        # Simulación de envío de correo
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_link}',
            'noreply@yourdomain.com',
            [user.email],
            fail_silently=False,
        )

        return Response({'detail': 'If an account with this email exists, a password reset link has been sent.'},
                        status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Vista para confirmar el reseteo de la contraseña.
    """
    permission_classes = [AllowAny]
    serializer_class = SetNewPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()
        if user is not None and token_generator.check_token(user, data['token']):
            user.set_password(data['password'])
            user.save()
            return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid token or user ID.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint de health check para verificar que la aplicación está funcionando.
    """
    from django.db import connection
    from sales.models import Order
    from products.models import Product

    try:
        # Verificar conexión a base de datos
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "error"

    # Contar registros
    try:
        orders_count = Order.objects.count()
        products_count = Product.objects.count()
    except Exception:
        orders_count = 0
        products_count = 0

    return Response({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'database': db_status,
        'orders_count': orders_count,
        'products_count': products_count,
        'version': '1.0.0'
    })

