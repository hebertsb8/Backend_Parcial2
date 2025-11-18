#!/bin/bash
# Script de inicio rápido para desarrollo local
# Uso: ./run_local.sh

echo "🚀 Iniciando Backend Django - Desarrollo Local"
echo "=============================================="

# Verificar si existe .env
if [ ! -f .env ]; then
    echo "📋 Creando archivo .env desde .env.local..."
    cp .env.local .env
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones locales"
fi

# Verificar si existe entorno virtual
if [ ! -d "venv" ]; then
    echo "🐍 Creando entorno virtual..."
    python -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/Scripts/activate  # Para Windows
# source venv/bin/activate    # Para Linux/Mac

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar migraciones
echo "🗄️  Ejecutando migraciones..."
python manage.py migrate

# Crear superusuario si no existe
echo "👤 Verificando superusuario..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell

# Ejecutar servidor
echo "🌐 Iniciando servidor de desarrollo..."
echo "   URL: http://10.128.114.55:8000"
echo "   Admin: http://10.128.114.55:8000/admin"
echo "   Credenciales admin: admin / admin123"
echo ""
echo "Para detener: Ctrl+C"
echo ""

python manage.py runserver 10.128.114.55:8000