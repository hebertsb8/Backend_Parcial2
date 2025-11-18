#!/usr/bin/env python
"""
Script de diagnóstico para Railway deployment
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django antes de cualquier import
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

print("=== Railway Deployment Diagnostics ===")
print(f"Python version: {sys.version}")
print(f"Django settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

try:
    django.setup()
    print("✅ Django setup successful")

    # Verificar configuración crítica
    print(f"DEBUG: {settings.DEBUG}")
    print(f"SECRET_KEY configured: {'Yes' if settings.SECRET_KEY else 'No'}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"DATABASE_URL configured: {'Yes' if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL else 'No'}")

    # Verificar base de datos
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✅ Database connection successful")

    # Verificar URLs
    from django.urls import reverse
    login_url = reverse('login')
    register_url = reverse('register')
    print(f"✅ URLs resolved: login={login_url}, register={register_url}")

    print("🎉 All diagnostics passed!")
    sys.exit(0)

except Exception as e:
    print(f"❌ Error during diagnostics: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)