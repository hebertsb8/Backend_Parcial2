#!/bin/bash
# Script de setup para producción en Railway con PostgreSQL
# Ejecutar después de importar la base de datos

echo "🚀 Iniciando setup de producción..."

# Aplicar migraciones (por si acaso)
echo "📦 Aplicando migraciones..."
python manage.py migrate

# Actualizar stock de productos
echo "📦 Actualizando stock de productos..."
python manage.py update_product_stock

# Generar datos de ventas para ML (sin reducir stock)
echo "📊 Generando datos de ventas para ML..."
python manage.py generate_demo_sales

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe
echo "👤 Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

echo "✅ Setup completado!"
echo ""
echo "📋 Comandos disponibles:"
echo "  • python manage.py update_product_stock  # Actualizar stock"
echo "  • python manage.py generate_demo_sales   # Generar datos ML"
echo "  • python manage.py retrain_sales_model   # Entrenar modelo ML"