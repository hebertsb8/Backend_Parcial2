from django.db import models
from django.core.exceptions import ValidationError
import os


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, help_text="Unique URL-friendly name for the category")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validaciones personalizadas"""
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'El nombre de la categoría no puede estar vacío.'})
        
        # Asegurar que el slug no tenga espacios
        if self.slug and ' ' in self.slug:
            raise ValidationError({'slug': 'El slug no puede contener espacios.'})


class Brand(models.Model):
    """
    Modelo para representar una marca de producto.
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'El nombre de la marca no puede estar vacío.'})


class Warranty(models.Model):
    """
    Modelo para gestionar las garantías de los productos.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Ej: Garantía Estándar 1 Año")
    duration_days = models.PositiveIntegerField(default=365, help_text="Duración de la garantía en días")
    details = models.TextField(blank=True, null=True, help_text="Detalles sobre qué cubre la garantía")

    class Meta:
        ordering = ['duration_days']
        verbose_name = "Garantía"
        verbose_name_plural = "Garantías"

    def __str__(self):
        return self.name


# --- CU27: Modelo Offer ---
class Offer(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    discount_percent = models.PositiveIntegerField(help_text="Porcentaje de descuento (1-100)")
    start_date = models.DateField()
    end_date = models.DateField()
    products = models.ManyToManyField('Product', related_name='offers')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Oferta"
        verbose_name_plural = "Ofertas"

    def __str__(self):
        return f"{self.title} ({self.discount_percent}% off)"


class ProductImage(models.Model):
    """
    Modelo para gestionar múltiples imágenes por producto.
    Permite hasta 3 imágenes por producto con orden personalizado.
    """
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', verbose_name="Imagen del producto")
    alt_text = models.CharField(max_length=255, blank=True, help_text="Texto alternativo para accesibilidad")
    order = models.PositiveIntegerField(default=0, help_text="Orden de visualización (0=primera)")
    is_main = models.BooleanField(default=False, help_text="Indica si es la imagen principal")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Imagen de Producto"
        verbose_name_plural = "Imágenes de Productos"
        unique_together = ['product', 'order']  # Evita órdenes duplicados por producto

    def __str__(self):
        return f"{self.product.name} - Imagen {self.order + 1}"

    def save(self, *args, **kwargs):
        # Si es la primera imagen del producto, marcarla como principal automáticamente
        if not ProductImage.objects.filter(product=self.product).exists():
            self.is_main = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Si eliminamos la imagen principal, marcar la siguiente como principal
        was_main = self.is_main
        super().delete(*args, **kwargs)
        
        if was_main:
            next_image = ProductImage.objects.filter(product=self.product).first()
            if next_image:
                next_image.is_main = True
                next_image.save()


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    warranty = models.ForeignKey(Warranty, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    # Campo image removido - ahora usamos ProductImage

    # Métricas adicionales para comparación y recomendaciones
    # Rating promedio (0.00 - 5.00). Nullable para compatibilidad con datos antiguos.
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    # Consumo energético estimado en kWh por año (puede ser None si no aplica)
    energy_kwh_per_year = models.FloatField(null=True, blank=True)

    # Campos de fecha automáticos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at'] # Muestra los productos más nuevos primero

    def __str__(self):
        return self.name
    
    def clean(self):
        """Validaciones personalizadas"""
        errors = {}
        
        # Validar precio
        if self.price is not None and self.price <= 0:
            errors['price'] = 'El precio debe ser mayor a 0.'
        
        # Validar nombre
        if not self.name or not self.name.strip():
            errors['name'] = 'El nombre del producto no puede estar vacío.'
        
        # Validar stock (aunque sea PositiveIntegerField, por si acaso)
        if self.stock < 0:
            errors['stock'] = 'El stock no puede ser negativo.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.full_clean()  # Ejecuta clean() y otras validaciones
        super().save(*args, **kwargs)
    
    @property
    def is_available(self):
        """Verifica si el producto está disponible"""
        return self.stock > 0
    
    @property
    def is_low_stock(self):
        """Verifica si el producto tiene stock bajo (menos de 10)"""
        return 0 < self.stock < 10
    
    @property
    def main_image(self):
        """Devuelve la imagen principal del producto"""
        return self.images.filter(is_main=True).first() or self.images.first()
    
    @property
    def image_url(self):
        """
        Devuelve la URL de la imagen principal si existe, None si no existe
        """
        main_img = self.main_image
        if main_img and main_img.image:
            try:
                if os.path.isfile(main_img.image.path):
                    return main_img.image.url
            except (ValueError, AttributeError):
                pass
        return None
    
    @property
    def all_image_urls(self):
        """Devuelve una lista de todas las URLs de imágenes válidas del producto"""
        urls = []
        for img in self.images.all():
            if img.image:
                try:
                    if os.path.isfile(img.image.path):
                        urls.append({
                            'url': img.image.url,
                            'alt_text': img.alt_text or self.name,
                            'is_main': img.is_main,
                            'order': img.order
                        })
                except (ValueError, AttributeError):
                    pass
        return urls
    
    @property
    def has_valid_image(self):
        """Verifica si el producto tiene al menos una imagen válida"""
        return self.main_image is not None
    
    def add_image(self, image_file, alt_text="", is_main=False, order=None):
        """Agrega una nueva imagen al producto"""
        if order is None:
            # Obtener el próximo orden disponible
            existing_orders = list(self.images.values_list('order', flat=True))
            order = 0
            while order in existing_orders:
                order += 1
        
        # Si es la primera imagen, marcarla como principal
        if not self.images.exists():
            is_main = True
        
        # Si se marca como principal, quitar la marca de otras imágenes
        if is_main:
            self.images.update(is_main=False)
        
        return ProductImage.objects.create(
            product=self,
            image=image_file,
            alt_text=alt_text,
            order=order,
            is_main=is_main
        )
    
    def delete_image(self, image_id=None):
        """Elimina una imagen específica o todas las imágenes del producto"""
        if image_id:
            try:
                img = self.images.get(id=image_id)
                img.delete()
                return True
            except ProductImage.DoesNotExist:
                return False
        else:
            # Eliminar todas las imágenes
            count = self.images.count()
            self.images.all().delete()
            return count > 0