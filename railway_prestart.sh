#!/bin/bash
# Script de pre-inicio para Railway
# Verifica configuración antes de iniciar Django

echo "🔍 Pre-inicio: Verificando configuración..."

# Verificar variables críticas
echo ""
echo "📋 Variables de entorno críticas:"
REQUIRED_VARS=("SECRET_KEY" "DATABASE_URL")
OPTIONAL_VARS=("DEBUG" "ALLOWED_HOSTS")

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ ERROR: Variable requerida faltante: $var"
        exit 1
    else
        echo "✅ $var: configurada"
    fi
done

for var in "${OPTIONAL_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️  $var: no configurada (usando valor por defecto)"
    else
        echo "✅ $var: ${!var:0:20}..."
    fi
done

# Verificar conectividad a base de datos
echo ""
echo "🗄️  Verificando base de datos..."
if python -c "
import os
import dj_database_url
from decouple import config

# Configurar Django settings mínimo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    DATABASE_URL = config('DATABASE_URL')
    db_config = dj_database_url.parse(DATABASE_URL)
    print('✅ DATABASE_URL parseada correctamente')
    print(f'   Host: {db_config.get(\"HOST\", \"unknown\")}')
    print(f'   Database: {db_config.get(\"NAME\", \"unknown\")}')
except Exception as e:
    print(f'❌ Error parseando DATABASE_URL: {e}')
    exit(1)
"; then
    echo "✅ Configuración de base de datos OK"
else
    echo "❌ Error en configuración de base de datos"
    exit 1
fi

# Verificar que Django puede importar settings
echo ""
echo "🐍 Verificando Django settings..."
if python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
try:
    from django.conf import settings
    settings.configure(
        SECRET_KEY='test-key',
        DEBUG=False,
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
        INSTALLED_APPS=['django.contrib.contenttypes']
    )
    print('✅ Django settings importados correctamente')
except Exception as e:
    print(f'❌ Error importando Django settings: {e}')
    exit(1)
"; then
    echo "✅ Django settings OK"
else
    echo "❌ Error en Django settings"
    exit 1
fi

echo ""
echo "🚀 Todas las verificaciones pasaron. Iniciando aplicación..."
exit 0