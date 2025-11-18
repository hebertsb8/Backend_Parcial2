"""
Generador de datos sintéticos para demostración del sistema de predicción de ventas.
Crea ventas realistas con patrones estacionales, tendencias y variabilidad.
"""
import os
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any

from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction, DatabaseError
from django.utils import timezone
from products.models import Product, Category, Brand, Warranty
from sales.models import Order, OrderItem, PaymentMethod

User = get_user_model()


class SalesDataGenerator:
    """
    Genera datos sintéticos de ventas con patrones realistas.
    """
    
    def __init__(self):
        # Generar al menos 36 meses de datos para mejores pruebas de series temporales y predicciones
        self.start_date = timezone.now() - timedelta(days=1095)  # ~36 meses atrás
        self.end_date = timezone.now()
        
    def _create_demo_products_if_needed(self) -> List[Product]:
        """Crea productos de demo si no existen y actualiza stock de productos existentes."""
        # Verificar si ya hay productos
        existing_products = list(Product.objects.all()[:30])
        if Product.objects.count() >= 15:  # Reducir el umbral para asegurar actualización de stock
            # Asegurar que incluso los productos existentes tengan stock y métricas pobladas
            for p in existing_products:
                # Actualizar stock si es 0 o None
                if p.stock == 0 or p.stock is None:
                    stock_options = [0, 0, 0] + list(range(5, 51)) + list(range(50, 201, 25))
                    p.stock = random.choice(stock_options)
                    p.save()
                self._ensure_product_metrics(p)
            return existing_products
        
        # Categorías específicas para tienda de electrodomésticos
        categories_data = [
            {'name': 'Heladeras', 'slug': 'heladeras'},
            {'name': 'Lavarropas', 'slug': 'lavarropas'},
            {'name': 'Microondas', 'slug': 'microondas'},
            {'name': 'Televisores', 'slug': 'televisores'},
            {'name': 'Cocinas', 'slug': 'cocinas'},
            {'name': 'Aire Acondicionado', 'slug': 'aire-acondicionado'},
            {'name': 'Pequeños Electrodomésticos', 'slug': 'pequenos-electrodomesticos'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, _ = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name']}
            )
            categories.append(category)
        
        # Precios ajustados para el mercado boliviano (en USD)
        # Basados en precios reales de electrodomésticos en Bolivia:
        # - Heladeras: 300-600 USD
        # - Lavarropas: 200-450 USD  
        # - Microondas: 30-120 USD
        # - TVs: 120-400 USD
        # - Aires acondicionados: 150-500 USD
        # - Pequeños electrodomésticos: 30-200 USD
        products_data = [
            {'name': 'Heladera No Frost 320L', 'price': 450.00, 'category': categories[0], 'popularity': 0.95},
            {'name': 'Heladera Top Mount 260L', 'price': 320.00, 'category': categories[0], 'popularity': 0.8},
            {'name': 'Lavarropas Carga Frontal 8kg', 'price': 380.00, 'category': categories[1], 'popularity': 0.9},
            {'name': 'Lavarropas Carga Superior 7kg', 'price': 280.00, 'category': categories[1], 'popularity': 0.7},
            {'name': 'Microondas 700W', 'price': 65.00, 'category': categories[2], 'popularity': 0.85},
            {'name': 'Microondas Convección 1000W', 'price': 120.00, 'category': categories[2], 'popularity': 0.6},
            {'name': 'Smart TV 50" 4K', 'price': 350.00, 'category': categories[3], 'popularity': 0.9},
            {'name': 'Smart TV 32" HD', 'price': 180.00, 'category': categories[3], 'popularity': 0.7},
            {'name': 'Cocina a Gas 4 Hornallas', 'price': 220.00, 'category': categories[4], 'popularity': 0.6},
            {'name': 'Anafe Eléctrico 2 Placas', 'price': 85.00, 'category': categories[4], 'popularity': 0.5},
            {'name': 'Aire Acondicionado Split 3000 Frig', 'price': 420.00, 'category': categories[5], 'popularity': 0.8},
            {'name': 'Aire Portátil 2000 Frig', 'price': 160.00, 'category': categories[5], 'popularity': 0.5},
            {'name': 'Licuadora Profesional', 'price': 45.00, 'category': categories[6], 'popularity': 0.7},
            {'name': 'Plancha Vertical', 'price': 35.00, 'category': categories[6], 'popularity': 0.4},
            {'name': 'Aspiradora Robot', 'price': 180.00, 'category': categories[6], 'popularity': 0.6},
        ]
        
        # Asegurar que existan algunas marcas y garantías por defecto
        default_brands = ['Generic', 'HomeTech', 'ElectroMax', 'SmartGoods']
        for b in default_brands:
            Brand.objects.get_or_create(name=b)

        default_warranties = [
            {'name': 'Garantía Estándar 1 Año', 'duration_days': 365},
            {'name': 'Garantía Extendida 2 Años', 'duration_days': 730}
        ]
        for w in default_warranties:
            Warranty.objects.get_or_create(name=w['name'], defaults={'duration_days': w['duration_days']})

        products = []
        for i, prod_data in enumerate(products_data):
            brand = None
            warranty = None
            try:
                # Intentamos leer marcas/garantías existentes
                brands = list(Brand.objects.all())
                warranties = list(Warranty.objects.all())
                if brands:
                    brand = brands[i % len(brands)]
                if warranties:
                    warranty = warranties[i % len(warranties)]
            except Exception:
                brands = []
                warranties = []

            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'price': Decimal(str(prod_data['price'])),
                    'category': prod_data['category'],
                    'description': f"Producto demo: {prod_data['name']}",
                    'brand': brand,
                    'warranty': warranty,
                }
            )
            # Asignar stock aleatorio si el producto es nuevo, tiene stock 0 o stock NULL
            if created or product.stock == 0 or product.stock is None:
                # Variar el stock: algunos productos con mucho stock, otros con poco, algunos sin stock
                stock_options = [0, 0, 0] + list(range(5, 51)) + list(range(50, 201, 25))  # Más productos con stock
                product.stock = random.choice(stock_options)
                product.save()
            # Asegurar que las métricas rating/energy existan o se actualicen
            self._ensure_product_metrics(product)
            # Guardar popularidad para uso interno (anexado dinámicamente)
            setattr(product, '_popularity', prod_data.get('popularity', 0.5))
            # Asignar imagen realista basada en el nombre del producto
            try:
                # Si no tiene imagen, descargar imagen real de Lorem Picsum
                if not product.image:
                    try:
                        import requests
                        from django.core.files.base import ContentFile
                        
                        # Función para generar keywords basados en el nombre del producto
                        def get_product_keywords(product_name):
                            name_lower = product_name.lower()
                            keywords = []
                            
                            # Keywords específicas por tipo de producto
                            if 'heladera' in name_lower or 'refrigerator' in name_lower:
                                keywords.extend(['fridge', 'refrigerator', 'kitchen', 'appliance', 'cooling'])
                            elif 'lavarropas' in name_lower or 'washing' in name_lower:
                                keywords.extend(['washing', 'machine', 'laundry', 'appliance', 'clothes'])
                            elif 'microondas' in name_lower or 'microwave' in name_lower:
                                keywords.extend(['microwave', 'kitchen', 'appliance', 'cooking', 'electronic'])
                            elif 'aire' in name_lower and 'acondicionado' in name_lower:
                                keywords.extend(['air', 'conditioner', 'cooling', 'appliance', 'climate'])
                            elif 'tv' in name_lower or 'television' in name_lower or 'smart tv' in name_lower:
                                keywords.extend(['television', 'tv', 'entertainment', 'electronic', 'screen'])
                            elif 'cocina' in name_lower or 'stove' in name_lower:
                                keywords.extend(['kitchen', 'stove', 'cooking', 'appliance', 'gas'])
                            elif 'anafe' in name_lower:
                                keywords.extend(['stove', 'kitchen', 'cooking', 'appliance', 'electric'])
                            elif 'licuadora' in name_lower or 'blender' in name_lower:
                                keywords.extend(['blender', 'kitchen', 'appliance', 'mixer', 'small'])
                            elif 'plancha' in name_lower:
                                keywords.extend(['iron', 'clothes', 'appliance', 'laundry', 'small'])
                            elif 'aspiradora' in name_lower or 'vacuum' in name_lower:
                                keywords.extend(['vacuum', 'cleaner', 'appliance', 'robot', 'small'])
                            else:
                                # Keywords genéricas para electrodomésticos
                                keywords.extend(['appliance', 'electronic', 'household', 'kitchen'])
                            
                            return keywords
                        
                        # Obtener keywords para este producto
                        product_keywords = get_product_keywords(product.name)
                        
                        # Seleccionar 2-3 keywords aleatorias para variar las imágenes
                        selected_keywords = random.sample(product_keywords, min(3, len(product_keywords)))
                        
                        # Crear URL de Lorem Picsum con keywords
                        keyword_string = ','.join(selected_keywords)
                        image_url = f'https://picsum.photos/400/300?random={random.randint(1, 1000)}&{keyword_string}'
                        
                        # Descargar la imagen
                        response = requests.get(image_url, timeout=10)
                        response.raise_for_status()
                        
                        # Crear nombre único para la imagen basado en el producto
                        safe_name = ''.join(c for c in product.name if c.isalnum() or c in ' _-').rstrip()
                        image_name = f"{safe_name.replace(' ', '_')}_{random.randint(1000, 9999)}.jpg"
                        
                        # Asignar la imagen al producto
                        product.image.save(image_name, ContentFile(response.content), save=True)
                        print(f"✓ Descargada imagen específica para: {product.name} (keywords: {keyword_string})")
                        
                    except ImportError:
                        print(f"⚠️  requests no instalado, usando placeholder para: {product.name}")
                        # Fallback al placeholder si requests no está disponible
                        try:
                            from django.conf import settings
                            import os
                            placeholder_path = os.path.join(settings.MEDIA_ROOT, 'products', 'placeholder.png')
                            if os.path.exists(placeholder_path):
                                image_name = f"product_{product.id}_placeholder.png"
                                with open(placeholder_path, 'rb') as f:
                                    image_content = f.read()
                                product.image.save(image_name, ContentFile(image_content), save=True)
                                print(f"✓ Asignada imagen placeholder a: {product.name}")
                        except Exception as e:
                            print(f"❌ Error con placeholder para {product.name}: {e}")
                    except Exception as e:
                        print(f"❌ Error descargando imagen para {product.name}: {e}")
            except Exception:
                # No bloquear la generación si falla guardar imagen
                pass

            products.append(product)
        
        return products

    def _ensure_product_metrics(self, product: Product):
        """
        Calcula y asigna rating y energy_kwh_per_year al producto si es necesario.
        No elimina ni modifica otros campos.
        """
        updated = False
        try:
            if getattr(product, 'rating', None) is None:
                pop = getattr(product, '_popularity', None)
                if pop is None:
                    base = 3.5 + min(1.5, float(product.price) / 2000.0)
                else:
                    base = 3.5 + (0.0 if pop is None else (pop - 0.5) * 2.0)
                rating_val = max(0.0, min(5.0, round(base + random.uniform(-0.3, 0.3), 2)))
                product.rating = Decimal(str(rating_val))
                updated = True
        except Exception:
            pass

        try:
            if getattr(product, 'energy_kwh_per_year', None) is None:
                cat = getattr(product.category, 'name', '').lower() if getattr(product, 'category', None) else ''
                if 'heladera' in cat:
                    energy = random.randint(250, 550)
                elif 'lavarropas' in cat:
                    energy = random.randint(50, 200)
                elif 'microondas' in cat:
                    energy = random.randint(50, 120)
                elif 'televisor' in cat:
                    energy = random.randint(30, 200)
                elif 'aire' in cat:
                    energy = random.randint(500, 2000)
                elif 'cocina' in cat:
                    energy = random.choice([0, random.randint(200, 800)])
                else:
                    energy = random.randint(20, 500)
                product.energy_kwh_per_year = float(energy)
                updated = True
        except Exception:
            pass

        if updated:
            try:
                product.save()
            except Exception:
                pass

    def _create_demo_payment_methods_if_needed(self) -> List[PaymentMethod]:
        """Crea métodos de pago de demo si no existen."""
        # Verificar si ya hay métodos de pago
        existing_methods = list(PaymentMethod.objects.all())
        if existing_methods:
            return existing_methods
        
        # Crear métodos de pago básicos
        payment_methods_data = [
            {'name': 'Tarjeta de Crédito/Débito (Stripe)'},
            {'name': 'Efectivo'},
            {'name': 'Transferencia Bancaria'},
        ]
        
        payment_methods = []
        for method_data in payment_methods_data:
            method, created = PaymentMethod.objects.get_or_create(
                name=method_data['name'],
                defaults={'is_active': True}
            )
            if created:
                print(f"✓ Creado método de pago: {method.name}")
            payment_methods.append(method)
        
        return payment_methods

        # Definir relaciones lógicas entre productos
        relations = [
            # Heladeras similares
            ('Heladera No Frost 320L', 'Heladera Top Mount 260L'),
            # Lavarropas similares
            ('Lavarropas Carga Frontal 8kg', 'Lavarropas Carga Superior 7kg'),
            # Microondas similares
            ('Microondas 700W', 'Microondas Convección 1000W'),
            # TVs similares
            ('Smart TV 50" 4K', 'Smart TV 32" HD'),
            # Aires acondicionados similares
            ('Aire Acondicionado Split 3000 Frig', 'Aire Portátil 2000 Frig'),
            # Cocinas similares
            ('Cocina a Gas 4 Hornallas', 'Anafe Eléctrico 2 Placas'),
            # Pequeños electrodomésticos relacionados
            ('Licuadora Profesional', 'Plancha Vertical'),
            ('Aspiradora Robot', 'Plancha Vertical'),
            ('Licuadora Profesional', 'Aspiradora Robot'),
        ]

        # Almacenar las relaciones en los productos como atributo temporal
        for prod1_name, prod2_name in relations:
            try:
                prod1 = next((p for p in products if p.name == prod1_name), None)
                prod2 = next((p for p in products if p.name == prod2_name), None)

                if prod1 and prod2:
                    # Almacenar relaciones como atributos temporales
                    if not hasattr(prod1, '_related_products'):
                        prod1._related_products = []
                    if not hasattr(prod2, '_related_products'):
                        prod2._related_products = []

                    prod1._related_products.append(prod2)
                    prod2._related_products.append(prod1)

                    print(f"  ✓ {prod1_name} ↔ {prod2_name}")
            except Exception as e:
                print(f"❌ Error configurando relación {prod1_name} -> {prod2_name}: {e}")

        print("✓ Relaciones de productos configuradas para recomendaciones")
    
    def _create_demo_customers_if_needed(self) -> List[User]:
        """Crea clientes de demo con datos completos si no existen."""
        # Verificar si ya hay clientes
        clients = list(User.objects.filter(profile__role='CLIENT')[:50])
        if len(clients) >= 30:
            return clients

        # Crear más clientes demo (hasta 50) con datos completos
        customers = []
        base_names = [
            ('Juan', 'Pérez'), ('María', 'García'), ('Carlos', 'López'), ('Ana', 'Martínez'),
            ('Luis', 'Rodríguez'), ('Sofía', 'Fernández'), ('Mateo', 'Gómez'), ('Valentina', 'Díaz'),
            ('Lucas', 'Torres'), ('Camila', 'Ruiz'), ('Diego', 'Alvarez'), ('Mía', 'Sánchez'),
            ('Martín', 'Romero'), ('Lucía', 'Ramírez'), ('Tomás', 'Vega'), ('Isabella', 'Rossi'),
            ('Andrés', 'Morales'), ('Gabriela', 'Silva'), ('Fernando', 'Ortiz'), ('Paula', 'Castro'),
            ('Roberto', 'Mendoza'), ('Carmen', 'Herrera'), ('José', 'Guerrero'), ('Elena', 'Flores'),
            ('Miguel', 'Rojas'), ('Rosa', 'Paredes'), ('Antonio', 'Vargas'), ('Teresa', 'León'),
            ('Francisco', 'Molina'), ('Patricia', 'Delgado'), ('Manuel', 'Aguilar'), ('Raquel', 'Soto'),
            ('Ángel', 'Delgado'), ('Cristina', 'Ortega'), ('Jesús', 'Rubio'), ('Pilar', 'Moreno'),
            ('Rafael', 'Serrano'), ('Dolores', 'Medina'), ('Javier', 'Castaño'), ('Concepción', 'Gil'),
            ('Alberto', 'Navarro'), ('Mercedes', 'Sáez'), ('Raúl', 'Hernández'), ('Isabel', 'Gallego'),
            ('Adrián', 'Santana'), ('Nuria', 'Iglesias'), ('Óscar', 'Cortés'), ('Montserrat', 'Lorenzo'),
        ]

        phone_prefixes = ['6', '7']
        cities = ['La Paz', 'Santa Cruz', 'Cochabamba', 'Sucre', 'Tarija', 'Potosí', 'Oruro', 'Beni', 'Pando']

        idx = 1
        for first, last in base_names[:50]:  # Limitar a 50 clientes
            username = f"cliente{idx}"
            email = f"{username}@demo.com"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last,
                }
            )

            if created:
                try:
                    user.set_password('demo123')
                    user.save()
                except Exception:
                    pass

                # Crear perfil completo
                try:
                    from api.models import Profile
                    phone = f"{random.choice(phone_prefixes)}{random.randint(1000000, 9999999)}"
                    address = f"Calle {random.randint(1, 999)}, {random.choice(cities)}"

                    profile, profile_created = Profile.objects.get_or_create(
                        user=user,
                        defaults={
                            'role': 'CLIENT',
                            'phone': phone,
                            'address': address,
                            'date_of_birth': self.start_date + timedelta(days=random.randint(365*18, 365*65)),
                        }
                    )

                    if profile_created:
                        print(f"✓ Creado perfil completo para: {first} {last}")

                except Exception as e:
                    print(f"❌ Error creando perfil para {first} {last}: {e}")

            customers.append(user)
            idx += 1

        return customers
    
    def _get_seasonal_multiplier(self, date: datetime) -> float:
        """
        Calcula un multiplicador estacional basado en el mes.
        - Diciembre (12): Alto (navidad)
        - Enero-Febrero: Bajo (post navidad)
        - Julio: Alto (medio año)
        - Resto: Normal
        """
        month = date.month
        
        if month == 12:
            return 1.5  # Pico navideño
        elif month in [1, 2]:
            return 0.7  # Bajón post navidad
        elif month in [7, 8]:
            return 1.3  # Temporada media alta
        elif month in [6, 11]:
            return 1.2  # Pre-vacaciones y pre-navidad
        else:
            return 1.0  # Normal
    
    def _get_trend_multiplier(self, date: datetime) -> float:
        """
        Calcula un multiplicador de tendencia (crecimiento en el tiempo).
        Simula crecimiento del negocio.
        """
        days_from_start = (date - self.start_date).days
        total_days = (self.end_date - self.start_date).days
        progress = days_from_start / total_days
        
        # Crecimiento del 50% durante el período
        return 1.0 + (progress * 0.5)
    
    def _get_weekday_multiplier(self, date: datetime) -> float:
        """
        Calcula multiplicador según día de la semana.
        - Fin de semana: Más ventas
        - Días laborables: Ventas normales
        """
        weekday = date.weekday()
        
        if weekday in [5, 6]:  # Sábado y Domingo
            return 1.3
        elif weekday == 4:  # Viernes
            return 1.1
        else:
            return 1.0
    
    def _generate_daily_sales_count(self, date: datetime) -> int:
        """
        Calcula cuántas ventas generar para un día específico.
        Aumentado para mejores datos de entrenamiento.
        """
        # Base: 15-40 ventas por día (aumentado para mejores predicciones)
        base_sales = random.randint(15, 40)
        
        # Aplicar multiplicadores
        seasonal = self._get_seasonal_multiplier(date)
        trend = self._get_trend_multiplier(date)
        weekday = self._get_weekday_multiplier(date)
        
        # Variabilidad aleatoria (80%-120%)
        random_factor = random.uniform(0.8, 1.2)
        
        # Calcular ventas finales
        sales_count = int(base_sales * seasonal * trend * weekday * random_factor)
        
        return max(3, sales_count)  # Mínimo 3 ventas
    
    def _generate_order_items(self, products: List[Product]) -> List[Dict[str, Any]]:
        """
        Genera items para una orden, considerando popularidad de productos.
        """
        # Número de items por orden (1-4)
        num_items = random.choices([1, 2, 3, 4], weights=[0.5, 0.3, 0.15, 0.05])[0]
        
        # Seleccionar productos según popularidad
        selected_products = random.choices(
            products,
            weights=[getattr(p, '_popularity', 0.5) for p in products],
            k=num_items
        )
        
        items = []
        for product in selected_products:
            quantity = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            items.append({
                'product': product,
                'quantity': quantity,
                'price': product.price
            })
        
        return items
    
    @transaction.atomic
    def generate_demo_data(self, clear_existing: bool = False) -> Dict[str, Any]:
        """
        Genera datos sintéticos de ventas de manera OPTIMIZADA.

        Args:
            clear_existing: Si es True, elimina las órdenes existentes antes de generar

        Returns:
            Dict con estadísticas de generación
        """
        if clear_existing:
            Order.objects.all().delete()
            print("✓ Órdenes existentes eliminadas")

        # Preparar datos
        products = self._create_demo_products_if_needed()
        customers = self._create_demo_customers_if_needed()
        payment_methods = self._create_demo_payment_methods_if_needed()

        print(f"✓ Preparando datos: {len(products)} productos, {len(customers)} clientes, {len(payment_methods)} métodos de pago")

        # OPTIMIZACIÓN: Generar TODOS los datos primero en memoria, luego bulk insert
        orders_to_create = []
        order_items_to_create = []

        current_date = self.start_date
        total_orders = 0
        total_revenue = Decimal('0.00')

        print("🚀 Generando datos de ventas en memoria...")

        while current_date <= self.end_date:
            daily_sales = self._generate_daily_sales_count(current_date)

            for _ in range(daily_sales):
                # Seleccionar cliente y método de pago aleatorios
                customer = random.choice(customers)
                payment_method = random.choices(
                    payment_methods,
                    weights=[0.8, 0.1, 0.1]  # 80% tarjeta, 10% efectivo, 10% transferencia
                )[0]

                # Generar items para esta orden
                items_data = self._generate_order_items(products)

                # Calcular total
                order_total = sum(
                    Decimal(str(item['quantity'])) * item['price']
                    for item in items_data
                )

                # Fecha específica para esta orden
                order_date = current_date + timedelta(
                    hours=random.randint(8, 20),
                    minutes=random.randint(0, 59)
                )

                # Crear objeto Order (aún no guardado)
                order = Order(
                    customer=customer,
                    payment_method=payment_method,
                    total_price=order_total,
                    status='COMPLETED',
                    created_at=order_date,
                    updated_at=order_date
                )
                orders_to_create.append(order)

                # Preparar items para esta orden (se asignarán después del bulk_create)
                for item_data in items_data:
                    order_item = OrderItem(
                        order=order,  # Se actualizará después
                        product=item_data['product'],
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )
                    order_items_to_create.append((order_item, order))

                total_orders += 1
                total_revenue += order_total

                # Mostrar progreso cada 1000 órdenes
                if total_orders % 1000 == 0:
                    print(f"📊 Generadas {total_orders} órdenes en memoria...")

            current_date += timedelta(days=1)

        print(f"✅ Generadas {total_orders} órdenes en memoria")
        print(f"💰 Ingresos totales proyectados: ${total_revenue:,.2f}")

        # OPTIMIZACIÓN: Bulk insert de órdenes
        print("💾 Insertando órdenes en base de datos...")
        created_orders = Order.objects.bulk_create(orders_to_create, batch_size=1000)
        print(f"✅ Insertadas {len(created_orders)} órdenes")

        # OPTIMIZACIÓN: Bulk insert de items de orden
        print("📦 Insertando items de orden...")
        order_items_objects = []
        for order_item, original_order in order_items_to_create:
            # Encontrar la orden creada correspondiente
            # Como bulk_create no preserva IDs, necesitamos mapear por contenido
            # Usamos el índice para mapear
            order_index = orders_to_create.index(original_order)
            if order_index < len(created_orders):
                order_item.order = created_orders[order_index]
                order_items_objects.append(order_item)

        # Bulk create de items
        OrderItem.objects.bulk_create(order_items_objects, batch_size=2000)
        print(f"✅ Insertados {len(order_items_objects)} items de orden")

        print("🎉 ¡Generación completada exitosamente!")
        print(f"📊 Estadísticas finales:")
        print(f"   • Órdenes: {total_orders}")
        print(f"   • Ingresos: ${total_revenue:,.2f}")
        print(f"   • Productos: {len(products)}")
        print(f"   • Clientes: {len(customers)}")

        return {
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'products_count': len(products),
            'customers_count': len(customers)
        }


def generate_sales_data(clear_existing: bool = False) -> Dict[str, Any]:
    """
    Función helper para generar datos de ventas demo.
    
    Args:
        clear_existing: Si es True, elimina las órdenes existentes antes de generar
        
    Returns:
        Dict con estadísticas de generación
        
    Ejemplo:
        >>> from sales.ml_data_generator import generate_sales_data
        >>> stats = generate_sales_data(clear_existing=True)
        >>> print(stats)
    """
    generator = SalesDataGenerator()
    return generator.generate_demo_data(clear_existing=clear_existing)


def update_products_metrics(limit: int = 0) -> Dict[str, int]:
    """
    Helper de módulo para actualizar métricas de productos (rating, energy_kwh_per_year).
    Útil para ejecutar desde manage.py shell: from sales.ml_data_generator import update_products_metrics; update_products_metrics()
    """
    products = list(Product.objects.all())
    checked = 0
    updated = 0
    gen = SalesDataGenerator()
    for p in products:
        if limit and checked >= limit:
            break
        before_rating = getattr(p, 'rating', None)
        before_energy = getattr(p, 'energy_kwh_per_year', None)
        gen._ensure_product_metrics(p)
        checked += 1
        if getattr(p, 'rating', None) != before_rating or getattr(p, 'energy_kwh_per_year', None) != before_energy:
            updated += 1

    return {'products_checked': checked, 'products_updated': updated}
