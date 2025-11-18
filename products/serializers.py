from rest_framework import serializers
from .models import Category, Product, Brand, Warranty, Offer, ProductImage
class OfferSerializer(serializers.ModelSerializer):
    # mantener products (PKs) para escritura, pero exponer detalle para lectura
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())
    products_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'description', 'discount_percent', 'start_date', 'end_date', 'products', 'products_detail', 'is_active']

    def get_products_detail(self, obj):
        # Representación ligera de productos dentro de una oferta para el cliente
        products = obj.products.all()
        data = []
        for p in products:
            # calcular image_url usando la nueva propiedad image_url
            try:
                image_url = p.image_url
            except Exception:
                image_url = None

            try:
                price_val = float(p.price) if p.price is not None else None
            except Exception:
                price_val = None

            discounted = None
            try:
                if price_val is not None:
                    discounted = price_val * (1 - (obj.discount_percent or 0) / 100.0)
            except Exception:
                discounted = None

            data.append({
                'id': p.id,
                'name': p.name,
                'price': price_val,
                'image_url': image_url,
                'discounted_price': discounted,
            })
        return data
import os


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializador para las imágenes de productos.
    """
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'order', 'is_main', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            try:
                if os.path.isfile(obj.image.path):
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(obj.image.url)
                    return obj.image.url
            except (ValueError, AttributeError, FileNotFoundError):
                pass
        return None


class WarrantySerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Garantías.
    """
    class Meta:
        model = Warranty
        fields = ['id', 'name', 'duration_days', 'details']


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Marcas.
    """
    class Meta:
        model = Brand
        fields = ['id', 'name', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Categorías.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo de Productos.
    """
    # Campos de solo lectura para info relacionada
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    
    # Detalles de objetos relacionados
    category_detail = CategorySerializer(source='category', read_only=True)
    brand_detail = BrandSerializer(source='brand', read_only=True)
    warranty_detail = WarrantySerializer(source='warranty', read_only=True)

    # Campos de imágenes múltiples
    main_image_url = serializers.SerializerMethodField()
    all_image_urls = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    has_valid_image = serializers.BooleanField(read_only=True)
    # Métricas nuevas expuestas al cliente
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True, allow_null=True)
    energy_kwh_per_year = serializers.FloatField(read_only=True, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock',
            'category',
            'brand',
            'warranty', # ID para escritura
            'category_name',
            'brand_name',
            'category_detail',
            'brand_detail',
            'warranty_detail',
            'rating',
            'energy_kwh_per_year',
            'images',
            'main_image_url',
            'all_image_urls',
            'has_valid_image',
            'created_at',
            'updated_at'
        ]
    
    def get_main_image_url(self, obj):
        return obj.image_url
    
    def get_all_image_urls(self, obj):
        return obj.all_image_urls
    
    def validate_image(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("La imagen no debe superar 5MB")
            
            valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
            ext = os.path.splitext(value.name)[1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError(
                    f"Formato de imagen no válido. Use: {', '.join(valid_extensions)}"
                )
        return value