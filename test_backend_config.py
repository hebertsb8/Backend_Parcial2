#!/usr/bin/env python
"""
Script de prueba para verificar que el backend Django funciona correctamente.
Ejecuta pruebas básicas de configuración y conectividad.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(__file__))

django.setup()

def test_basic_setup():
    """Prueba que Django se configure correctamente."""
    print("✅ Django setup successful")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   SECRET_KEY configured: {'Yes' if settings.SECRET_KEY else 'No'}")
    print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"   DATABASE_URL configured: {'Yes' if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL else 'No'}")

def test_database_connection():
    """Prueba la conexión a la base de datos."""
    from django.db import connection
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_urls():
    """Prueba que las URLs se resuelvan correctamente."""
    from django.urls import reverse
    try:
        # Probar algunas URLs críticas
        login_url = reverse('login')
        register_url = reverse('register')
        print("✅ URL resolution successful")
        print(f"   Login URL: {login_url}")
        print(f"   Register URL: {register_url}")
        return True
    except Exception as e:
        print(f"❌ URL resolution failed: {e}")
        return False

def main():
    print("🚀 Testing Django Backend Configuration")
    print("=" * 50)

    test_basic_setup()
    print()

    db_ok = test_database_connection()
    print()

    urls_ok = test_urls()
    print()

    if db_ok and urls_ok:
        print("🎉 All tests passed! Backend should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check configuration.")
        return 1

if __name__ == '__main__':
    sys.exit(main())