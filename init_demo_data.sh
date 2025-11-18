#!/bin/bash
# Script para inicializar datos demo en producción
# Uso: bash init_demo_data.sh

echo "🚀 Inicializando datos demo en producción..."

# Verificar si ya hay órdenes
ORDER_COUNT=$(python manage.py shell -c "from sales.models import Order; print(Order.objects.count())")

if [ "$ORDER_COUNT" -gt 0 ]; then
    echo "⚠️  Ya existen $ORDER_COUNT órdenes. ¿Deseas continuar? (yes/no)"
    read -r response
    if [ "$response" != "yes" ]; then
        echo "❌ Operación cancelada"
        exit 1
    fi
fi

echo "🏗️  Generando datos demo..."
python manage.py generate_demo_sales

echo "✅ Inicialización completada!"