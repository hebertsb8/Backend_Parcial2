#!/usr/bin/env python
"""
Script para verificar la configuración de Firebase híbrida
Ejecutar después de configurar las variables de entorno en .env
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

from django.conf import settings
from notifications.firebase_service import FirebaseService

def check_env_vars():
    """Verificar que las variables de entorno estén configuradas"""
    print("🔍 Verificando variables de entorno...")

    required_vars = [
        'FIREBASE_CREDENTIALS_PATH',
        'FIREBASE_PUBLIC_API_KEY',
        'FIREBASE_AUTH_DOMAIN',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET',
        'FIREBASE_MESSAGING_SENDER_ID',
        'FIREBASE_APP_ID'
    ]

    missing_vars = []
    for var in required_vars:
        value = getattr(settings, var, None)
        if not value or value.startswith('tu_') or value.startswith('pk_test_') or value.startswith('sk_test_'):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {value[:20]}..." if len(str(value)) > 20 else f"✅ {var}: {value}")

    if missing_vars:
        print(f"\n❌ Variables faltantes o con valores de ejemplo: {', '.join(missing_vars)}")
        return False

    return True

def check_firebase_credentials():
    """Verificar que el archivo de credenciales de Firebase existe"""
    print("\n🔍 Verificando archivo de credenciales de Firebase...")

    credentials_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
    if not credentials_path:
        print("❌ FIREBASE_CREDENTIALS_PATH no configurado")
        return False

    full_path = BASE_DIR / credentials_path
    if not full_path.exists():
        print(f"❌ Archivo de credenciales no encontrado: {full_path}")
        return False

    print(f"✅ Archivo de credenciales encontrado: {full_path}")
    return True

def check_firebase_service():
    """Verificar que el servicio de Firebase se inicializa correctamente"""
    print("\n🔍 Verificando inicialización del servicio de Firebase...")

    try:
        firebase_service = FirebaseService()
        if firebase_service.is_initialized():
            print("✅ Servicio de Firebase inicializado correctamente")
            return True
        else:
            print("❌ Servicio de Firebase no inicializado")
            return False
    except Exception as e:
        print(f"❌ Error al inicializar servicio de Firebase: {e}")
        return False

def check_api_endpoint():
    """Verificar que el endpoint de configuración de Firebase funciona"""
    print("\n🔍 Verificando endpoint de configuración de Firebase...")

    from django.test import Client
    client = Client()

    try:
        response = client.get('/api/notifications/firebase-config/')
        if response.status_code == 200:
            data = response.json()
            required_keys = ['apiKey', 'authDomain', 'projectId', 'storageBucket', 'messagingSenderId', 'appId']
            if all(key in data for key in required_keys):
                print("✅ Endpoint de configuración de Firebase funcionando correctamente")
                return True
            else:
                print(f"❌ Endpoint no devuelve todas las claves requeridas. Faltan: {[k for k in required_keys if k not in data]}")
                return False
        else:
            print(f"❌ Endpoint devolvió código de estado: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al acceder al endpoint: {e}")
        return False

def main():
    print("🚀 Verificación de configuración de Firebase híbrida\n")

    checks = [
        check_env_vars,
        check_firebase_credentials,
        check_firebase_service,
        check_api_endpoint
    ]

    passed = 0
    for check in checks:
        if check():
            passed += 1

    print(f"\n📊 Resultado: {passed}/{len(checks)} verificaciones pasaron")

    if passed == len(checks):
        print("🎉 ¡Configuración de Firebase híbrida completada exitosamente!")
        print("\n📝 Próximos pasos:")
        print("1. Actualiza tu frontend para usar el nuevo hook de notificaciones")
        print("2. Prueba el registro de tokens FCM desde el frontend")
        print("3. Verifica que las notificaciones push funcionen")
    else:
        print("⚠️  Configuración incompleta. Revisa los errores arriba y completa la configuración.")

if __name__ == '__main__':
    main()