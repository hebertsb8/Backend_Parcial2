#!/usr/bin/env python
"""
Script para asignar stock aleatorio a todos los productos existentes.
Ejecutar con: python scripts/assign_stock.py
"""
import os
import sys
import django
import random

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from products.models import Product

def assign_random_stock():
    """Asigna stock aleatorio (1-100) a todos los productos que tienen stock=0"""
    products = Product.objects.filter(stock=0)
    updated_count = 0

    for product in products:
        old_stock = product.stock
        new_stock = random.randint(1, 100)
        product.stock = new_stock
        product.save()
        print(f"Producto '{product.name}': stock {old_stock} -> {new_stock}")
        updated_count += 1

    print(f"\nTotal productos actualizados: {updated_count}")
    return updated_count

if __name__ == '__main__':
    assign_random_stock()