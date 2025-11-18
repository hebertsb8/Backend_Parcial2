#!/usr/bin/env python3
"""
Script para verificar el estado de tokens FCM registrados
Ejecutar: python check_fcm_tokens.py
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from notifications.models import DeviceToken
from django.contrib.auth.models import User
from django.db.models import Count

def check_fcm_tokens():
    """Verificar el estado de tokens FCM en la base de datos"""

    print("🔍 VERIFICANDO TOKENS FCM REGISTRADOS")
    print("=" * 50)

    # Estadísticas generales
    total_tokens = DeviceToken.objects.count()
    active_tokens = DeviceToken.objects.filter(is_active=True).count()

    print(f"📊 Total de tokens registrados: {total_tokens}")
    print(f"✅ Tokens activos: {active_tokens}")

    # Tokens por plataforma
    tokens_por_plataforma = DeviceToken.objects.values('platform').annotate(count=Count('id'))
    print("\n📱 Tokens por plataforma:")
    for item in tokens_por_plataforma:
        print(f"   {item['platform']}: {item['count']}")

    # Usuarios con tokens
    usuarios_con_tokens = User.objects.filter(device_tokens__is_active=True).distinct().count()
    print(f"\n👥 Usuarios con tokens activos: {usuarios_con_tokens}")

    # Detalles de tokens si existen
    if total_tokens > 0:
        print("\n🔍 ÚLTIMOS TOKENS REGISTRADOS:")
        print("-" * 40)

        for token in DeviceToken.objects.all()[:5]:
            print(f"👤 Usuario: {token.user.username}")
            print(f"📱 Plataforma: {token.platform}")
            print(f"✅ Activo: {token.is_active}")
            print(f"🕒 Creado: {token.created_at}")
            print(f"🔑 Token: {token.token[:50]}...")
            print("-" * 40)

    # Resumen final
    print("\n" + "=" * 50)
    if total_tokens == 0:
        print("❌ NO HAY TOKENS FCM REGISTRADOS")
        print("💡 Los usuarios necesitan registrar sus dispositivos desde Flutter/Web")
    else:
        print(f"✅ HAY {total_tokens} TOKENS REGISTRADOS ({active_tokens} activos)")
        print("🚀 Las notificaciones push están listas para funcionar")

    print("=" * 50)

if __name__ == "__main__":
    check_fcm_tokens()