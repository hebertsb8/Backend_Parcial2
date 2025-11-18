"""
Management command para actualizar stock de productos existentes.
Uso: python manage.py update_product_stock
"""
from django.core.management.base import BaseCommand
import random

from products.models import Product


class Command(BaseCommand):
    help = 'Actualiza el stock de productos existentes con valores aleatorios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔄 Actualizando stock de productos...'))
        
        products = Product.objects.all()
        updated_count = 0
        
        for product in products:
            old_stock = product.stock
            # Variar el stock: algunos productos con mucho stock, otros con poco, algunos sin stock
            stock_options = [0, 0, 0] + list(range(5, 51)) + list(range(50, 201, 25))
            product.stock = random.choice(stock_options)
            product.save()
            self.stdout.write(f"  {product.name}: {old_stock} → {product.stock}")
            updated_count += 1
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Actualizados {updated_count} productos'))
        self.stdout.write('') 