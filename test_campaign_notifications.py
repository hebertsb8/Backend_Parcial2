# test_campaign_notifications.py
"""
Script para probar el sistema de campañas de notificaciones.
Crea una campaña y envía notificaciones a usuarios con tokens FCM.
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from notifications.models import NotificationCampaign, DeviceToken
from notifications.notification_service import NotificationService

def test_campaign_system():
    """Prueba el sistema de campañas de notificaciones"""
    print("=== Probando Sistema de Campañas de Notificaciones ===\n")

    # 1. Verificar usuarios con tokens
    users_with_tokens = User.objects.filter(device_tokens__is_active=True).distinct()
    print(f"Usuarios con tokens FCM activos: {users_with_tokens.count()}")

    if not users_with_tokens.exists():
        print("❌ No hay usuarios con tokens FCM activos. Registra algunos tokens primero.")
        return

    for user in users_with_tokens:
        token_count = DeviceToken.objects.filter(user=user, is_active=True).count()
        print(f"  - {user.username}: {token_count} tokens")

    # 2. Crear una campaña de prueba
    print("\n--- Creando campaña de prueba ---")
    campaign = NotificationCampaign.objects.create(
        title="Campaña de Prueba - Oferta Especial",
        description="Notificación de prueba para verificar el sistema de campañas",
        campaign_type=NotificationCampaign.CampaignType.MANUAL,
        total_users=users_with_tokens.count()
    )
    print(f"✅ Campaña creada: {campaign.title} (ID: {campaign.id})")

    # 3. Enviar notificaciones usando el servicio
    print("\n--- Enviando notificaciones ---")
    result = NotificationService.send_notification_to_users(
        users=list(users_with_tokens),
        title="¡Oferta Especial!",
        body="Tenemos una oferta especial para ti. ¡No te la pierdas!",
        notification_type='CUSTOM',
        campaign_title=campaign.title,
        campaign_description=campaign.description,
        created_by=None  # No hay usuario admin en este script
    )

    print("📊 Resultados del envío:")
    print(f"  - Usuarios objetivo: {result['total_users']}")
    print(f"  - Usuarios exitosos: {result['successful_users']}")
    print(f"  - Usuarios fallidos: {result['failed_users']}")
    print(f"  - Envíos exitosos: {result['successful_sends']}")
    print(f"  - Envíos fallidos: {result['failed_sends']}")

    # 4. Actualizar estadísticas de la campaña
    campaign.update_statistics()
    print("\n✅ Estadísticas de campaña actualizadas:")
    print(f"  - Envíos exitosos: {campaign.successful_sends}")
    print(f"  - Envíos fallidos: {campaign.failed_sends}")
    print(f"  - Tasa de éxito: {campaign.successful_sends}/{campaign.total_users}")

    # 5. Mostrar notificaciones fallidas
    failed_notifications = campaign.notifications.filter(status='FAILED')
    if failed_notifications.exists():
        print(f"\n❌ Notificaciones fallidas ({failed_notifications.count()}):")
        for notification in failed_notifications:
            print(f"  - Usuario: {notification.user.username}")
            print(f"    Error: {notification.error_message}")
            print(f"    Estado: {notification.status}")
    else:
        print("\n✅ No hay notificaciones fallidas")

    # 6. Mostrar notificaciones enviadas
    sent_notifications = campaign.notifications.filter(status='SENT')
    if sent_notifications.exists():
        print(f"\n✅ Notificaciones enviadas exitosamente ({sent_notifications.count()}):")
        for notification in sent_notifications[:3]:  # Mostrar solo las primeras 3
            print(f"  - Usuario: {notification.user.username}")
            print(f"    Enviada: {notification.sent_at}")
    else:
        print("\n❌ No hay notificaciones enviadas")

    print("\n🎉 Prueba completada!")
    print(f"Campaña ID: {campaign.id} - Puedes revisar las notificaciones en /api/notifications/campaigns/{campaign.id}/")

if __name__ == "__main__":
    test_campaign_system()