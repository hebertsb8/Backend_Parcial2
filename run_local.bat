@echo off
REM Script de inicio rápido para desarrollo local en Windows
REM Uso: run_local.bat

echo 🚀 Iniciando Backend Django - Desarrollo Local
echo ==============================================

REM Verificar si existe .env
if not exist .env (
    echo 📋 Creando archivo .env desde .env.local...
    copy .env.local .env
    echo ⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones locales
    timeout /t 3 >nul
)

REM Verificar si existe entorno virtual
if not exist venv (
    echo 🐍 Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt

REM Ejecutar migraciones
echo 🗄️  Ejecutando migraciones...
python manage.py migrate

REM Crear superusuario si no existe
echo 👤 Verificando superusuario...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superusuario existe' if User.objects.filter(username='admin').exists() else 'Creando superusuario...'); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

REM Ejecutar servidor
echo.
echo 🌐 Iniciando servidor de desarrollo...
echo    URL: http://10.128.114.55:8000
echo    Admin: http://10.128.114.55:8000/admin
echo    Credenciales admin: admin / admin123
echo.
echo Para detener: Ctrl+C
echo.

python manage.py runserver 10.128.114.55:8000