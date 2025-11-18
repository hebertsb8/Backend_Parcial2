from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, BrandViewSet, WarrantyViewSet, OfferViewSet, ProductImageViewSet

# Importar vistas de recomendaciones desde sales app
from sales.views_recommendations import (
    get_user_recommendations, 
    get_similar_products,
    get_trending_products,
    get_frequently_bought_together
)

# Creamos un router que generará las URLs automáticamente
router = DefaultRouter()
router.register(r'warranties', WarrantyViewSet, basename='warranty')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'categories', CategoryViewSet, basename='category')
# No registramos 'products' en el router para evitar colisión con rutas ML
# router.register(r'products', ProductViewSet, basename='product')
router.register(r'offers', OfferViewSet, basename='offer')
router.register(r'product-images', ProductImageViewSet, basename='product-image')

urlpatterns = [
    # ========================================
    # 🔗 ALIAS PARA COMPATIBILIDAD CON FRONTEND
    # ========================================
    # El frontend está llamando a estas URLs bajo /api/shop/products/ml/
    # pero las vistas están en sales app bajo /api/sales/ml/
    # Estas rutas actúan como aliases para mantener compatibilidad
    
    # Recomendaciones personalizadas para el usuario actual
    # Frontend: GET /api/shop/products/ml/recommendations/personalized/?limit=8
    # Backend real: /api/sales/ml/recommendations/
    path('products/ml/recommendations/personalized/', get_user_recommendations, name='products-recommendations-personalized'),
    
    # Productos similares a uno específico
    # Frontend: GET /api/shop/products/ml/recommendations/similar/<id>/?limit=6
    # Backend real: /api/sales/ml/similar-products/<id>/
    path('products/ml/recommendations/similar/<int:product_id>/', get_similar_products, name='products-recommendations-similar'),
    
    # Productos en tendencia
    # Frontend: GET /api/shop/products/ml/recommendations/trending/?limit=10
    # Backend real: /api/sales/ml/trending/
    path('products/ml/recommendations/trending/', get_trending_products, name='products-recommendations-trending'),
    
    # Productos frecuentemente comprados juntos
    # Frontend: GET /api/shop/products/ml/recommendations/bought-together/<id>/?limit=5
    # Backend real: /api/sales/ml/bought-together/<id>/
    path('products/ml/recommendations/bought-together/<int:product_id>/', get_frequently_bought_together, name='products-recommendations-bought-together'),

    # ========================================
    # 🛍️ RUTAS MANUALES PARA PRODUCTOS
    # ========================================
    # Definidas manualmente para evitar colisión con rutas ML que empiezan con 'ml/'
    
    # Lista y creación de productos
    path('products/', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    
    # Detalle, actualización y eliminación de productos
    # Solo captura IDs numéricos, no 'ml' u otras strings
    path('products/<int:pk>/', ProductViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='product-detail'),
    
    # Subida de imágenes para productos
    path('products/<int:pk>/upload_image/', ProductViewSet.as_view({'post': 'upload_image'}), name='product-upload-image'),
    
    # Eliminación de imágenes de productos
    path('products/<int:pk>/delete_image/', ProductViewSet.as_view({'delete': 'delete_image'}), name='product-delete-image'),
    
    # Limpieza de imágenes rotas
    path('products/clean_broken_images/', ProductViewSet.as_view({'post': 'clean_broken_images'}), name='product-clean-broken-images'),

    # Router de productos (debe ir después de las rutas específicas para no interferir)
    path('', include(router.urls)),
]