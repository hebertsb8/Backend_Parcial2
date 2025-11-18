#!/bin/bash
# Script de despliegue para producción
# Ejecutar: bash deploy_production.sh

echo "🚀 Iniciando despliegue para producción..."

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio raíz del proyecto Django"
    exit 1
fi

# Verificar variables de entorno
echo "🔍 Verificando configuración..."
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  DATABASE_URL no está configurada, usando SQLite como alternativa"
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar migraciones
echo "🗄️  Ejecutando migraciones de base de datos..."
python manage.py migrate

# Recopilar archivos estáticos
echo "📂 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Entrenar modelos ML (opcional)
if [ "$ENABLE_ML_TRAINING" = "True" ]; then
    echo "🤖 Entrenando modelos ML..."
    python train_ml_models.py
fi

# Verificar configuración
echo "🔧 Verificando configuración..."
python manage.py check --deploy

# Crear superusuario si no existe (opcional)
echo "👤 Verificando superusuario..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell

echo ""
echo "✅ DESPLIEGUE COMPLETADO"
echo ""
echo "📋 Verificación final:"
echo "• Base de datos: $(python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings'); import django; django.setup(); from django.db import connection; print(connection.vendor)")"
echo "• Modelos ML: $(ls -la ml_models/*.pkl 2>/dev/null | wc -l) archivos encontrados"
echo "• Archivos estáticos: $(find staticfiles -type f 2>/dev/null | wc -l) archivos recopilados"
echo ""
echo "🌐 El servidor está listo para producción"
echo "Ejecuta: python manage.py runserver 0.0.0.0:8000"