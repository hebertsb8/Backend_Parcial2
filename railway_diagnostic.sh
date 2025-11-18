#!/bin/bash
# Script de diagnóstico para Railway
echo "🔍 Diagnóstico de Railway Backend"
echo "================================="

# Verificar variables de entorno críticas
echo ""
echo "📋 Variables de entorno:"
echo "DEBUG: $DEBUG"
echo "SECRET_KEY: ${SECRET_KEY:0:10}..."
echo "DATABASE_URL: ${DATABASE_URL:0:20}..."
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"

# Verificar conectividad a base de datos
echo ""
echo "🗄️  Verificando base de datos..."
python manage.py dbshell --command="SELECT 1;" 2>/dev/null && echo "✅ Base de datos conectada" || echo "❌ Error de conexión a BD"

# Verificar migraciones
echo ""
echo "📊 Verificando migraciones..."
python manage.py showmigrations | grep -E "\[ \]" && echo "⚠️  Hay migraciones pendientes" || echo "✅ Todas las migraciones aplicadas"

# Verificar archivos estáticos
echo ""
echo "📁 Verificando archivos estáticos..."
python manage.py collectstatic --noinput --dry-run | grep -q "0 static files" && echo "⚠️  No hay archivos estáticos" || echo "✅ Archivos estáticos OK"

# Probar que Django responde
echo ""
echo "🚀 Probando Django..."
timeout 10 python manage.py runserver 0.0.0.0:8000 &
SERVER_PID=$!
sleep 3
curl -s http://localhost:8000/api/health/ && echo "✅ Django responde" || echo "❌ Django no responde"
kill $SERVER_PID 2>/dev/null

echo ""
echo "🏁 Diagnóstico completado"