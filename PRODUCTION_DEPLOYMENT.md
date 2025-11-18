# 🚀 Guía de Despliegue en Producción - Railway + PostgreSQL

## Problema Resuelto

El generador de datos sintéticos no asignaba stock correctamente a los productos al importar la base de datos en producción. Los productos se importaban con `stock = 0` o `NULL`.

## Solución Implementada

### 1. Modificaciones al Generador de Datos Sintéticos

- **`sales/ml_data_generator.py`**: Actualizado para manejar casos donde `stock` es `NULL` (común en PostgreSQL)
- **Reducción de stock deshabilitada**: El generador ya no reduce el stock real al crear órdenes históricas

### 2. Nuevo Comando de Management

```bash
python manage.py update_product_stock
```

Actualiza el stock de todos los productos existentes con valores aleatorios realistas.

### 3. Script de Setup Automático

```bash
./scripts/setup_production.sh
```

Ejecuta todo el setup necesario después de importar la base de datos.

## 📋 Pasos para Despliegue en Railway

### 1. Exportar Base de Datos Local

```bash
# Crear backup de SQLite
cp db.sqlite3 db_backup.sqlite3

# O exportar a SQL si es necesario
python manage.py dumpdata > data.json
```

### 2. Configurar Railway

- Crear proyecto en Railway
- Configurar PostgreSQL database
- Configurar variables de entorno:
  ```
  DATABASE_URL=postgresql://...
  SECRET_KEY=tu_secret_key_segura
  DEBUG=False
  # Otras variables necesarias
  ```

### 3. Desplegar Código

```bash
# Subir código a Git y conectar con Railway
git add .
git commit -m "Ready for production"
git push origin main
```

### 4. Setup en Producción

Después de que Railway complete el despliegue:

```bash
# Conectar via Railway CLI o shell
railway shell

# Ejecutar setup
./scripts/setup_production.sh
```

O manualmente:

```bash
python manage.py migrate
python manage.py update_product_stock
python manage.py generate_demo_sales
python manage.py collectstatic --noinput
```

### 5. Verificar

```bash
# Verificar stock de productos
python manage.py shell -c "from products.models import Product; [print(f'{p.name}: {p.stock}') for p in Product.objects.all()]"

# Verificar que las APIs funcionen
curl https://tu-app.railway.app/api/shop/products/
```

## 🔧 Comandos Útiles en Producción

```bash
# Actualizar stock si es necesario
python manage.py update_product_stock

# Regenerar datos ML
python manage.py generate_demo_sales

# Entrenar modelo de predicción
python manage.py retrain_sales_model
```

## ⚠️ Notas Importantes

1. **Stock Management**: El stock se maneja correctamente tanto en desarrollo como producción
2. **Datos ML**: Los datos históricos no afectan el stock disponible
3. **PostgreSQL Compatibility**: El código maneja diferencias entre SQLite y PostgreSQL
4. **Performance**: Los comandos están optimizados para entornos de producción

## 🐛 Troubleshooting

### Stock en cero después del despliegue

```bash
# Ejecutar actualización de stock
python manage.py update_product_stock
```

### Error de base de datos

```bash
# Verificar conexión
python manage.py dbshell
# O verificar settings
python manage.py check
```

### Problemas con ML

```bash
# Regenerar datos
python manage.py generate_demo_sales --clear
```
