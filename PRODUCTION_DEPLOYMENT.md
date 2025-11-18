# 🚀 Guía Completa de Despliegue en Producción

## 🎯 Visión General

Esta guía cubre el despliegue completo del backend Django con:

- ✅ PostgreSQL (Railway)
- ✅ Configuración de credenciales en base64
- ✅ Modelos ML entrenados
- ✅ Variables de entorno para producción
- ✅ Archivos de configuración para múltiples plataformas

## 📋 Requisitos Previos

- Python 3.11+
- PostgreSQL (Railway recomendado)
- Redis (opcional, para cache)
- Cuentas en servicios externos:
  - Firebase (notificaciones push)
  - Stripe (pagos)
  - Google Cloud (opcional, Speech-to-Text)

## 🔧 Configuración de Variables de Entorno

### 1. Template de Producción

Copia el template incluido en el repositorio:

```bash
cp .env.production.template .env
```

### 2. Variables Esenciales

#### Base de Datos (Railway PostgreSQL)

```bash
DATABASE_URL=postgresql://postgres:cYpvNcrPVGUMNXKVgkVxeJfEkPJHPbFq@nozomi.proxy.rlwy.net:40214/railway
```

#### Django Settings

```bash
SECRET_KEY=django-insecure-production-key-change-this-in-production-2025-unique-key
DEBUG=False
ALLOWED_HOSTS=backendparcial2-production.up.railway.app,*.up.railway.app,*.railway.app
CORS_ALLOWED_ORIGINS=https://backendparcial2-production.up.railway.app
CORS_ALLOW_CREDENTIALS=True
```

#### Stripe (Producción)

```bash
STRIPE_PUBLIC_KEY=pk_live_XXXXXXXXXXXXXXXXXX
STRIPE_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXX
```

#### Firebase

```bash
FIREBASE_CREDENTIALS_PATH=./firebase-credentials-production.json
FIREBASE_PUBLIC_API_KEY=XXXXXXXXXXXXXXXXXX
FIREBASE_AUTH_DOMAIN=tu-proyecto.firebaseapp.com
FIREBASE_PROJECT_ID=tu-project-id
FIREBASE_STORAGE_BUCKET=tu-proyecto.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=XXXXXXXXXXXX
```

## 🗄️ Configuración de Credenciales Codificadas

### 1. Firebase Credentials en Base64

```bash
# 1. Obtener credenciales de Firebase Console
# 2. Codificar en base64
base64 firebase-credentials.json > firebase_credentials_base64.txt

# 3. El contenido codificado se usa en la variable de entorno
FIREBASE_CREDENTIALS_BASE64=ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIs...
```

### 2. Google Cloud Credentials (opcional)

```bash
base64 google-cloud-credentials.json > gcp_credentials_base64.txt
```

## 🚀 Opciones de Despliegue

### Opción 1: Railway (Recomendado)

1. Conecta tu repositorio GitHub a Railway
2. Railway detectará automáticamente `railway.toml`
3. Configura variables de entorno en Railway Dashboard
4. El despliegue se ejecuta automáticamente

### Opción 2: Render

````yaml
# render.yaml
## 🚀 **Opciones de Despliegue**

### Opción 1: Despliegue Rápido (Recomendado para Testing)
```yaml
services:
  - type: web
    name: backend-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: FAST_MODE=true python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:$PORT
````

**Ventajas:**

- ✅ Inicio en 30-60 segundos
- ✅ Sin descarga de imágenes
- ✅ Datos demo listos en 2-3 minutos

### Opción 2: Despliegue Completo (Para Producción)

```yaml
services:
  - type: web
    name: backend-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:$PORT
```

**Nota:** El despliegue completo puede tardar 5-10 minutos por la descarga de imágenes.

### Variables de Entorno para Optimización

```bash
# Modo rápido (sin imágenes)
FAST_MODE=true

# Para generar datos demo después del despliegue
GENERATE_DEMO_DATA=true
```

````

### Opción 3: Heroku

```bash
heroku create tu-app-name
heroku config:set VARIABLE=valor
git push heroku main
````

### Opción 4: VPS Manual

```bash
# Usar el script incluido
bash deploy_production.sh
```

## 🤖 Modelos de Machine Learning

### Entrenamiento Automático

```bash
# Entrenar modelos ML
python train_ml_models.py

# O usar el comando de Django
python manage.py ml_train
```

### Modelos Incluidos

- ✅ **Predictor de Ventas**: Regresión lineal con features temporales
- ✅ **Recomendador de Productos**: Basado en similitud coseno
- ✅ **Datos de Entrenamiento**: Generados automáticamente

### Reentrenamiento

Los modelos se reentrenan automáticamente cada 7 días si `ENABLE_ML_TRAINING=True`.

## 📊 Problema Resuelto - Stock de Productos

### Issue Original

El generador de datos sintéticos no asignaba stock correctamente en PostgreSQL.

### Solución Implementada

- **`sales/ml_data_generator.py`**: Maneja casos `NULL` en PostgreSQL
- **Comando nuevo**: `python manage.py update_product_stock`
- **Script automático**: `./scripts/setup_production.sh`

## 🔒 Checklist de Seguridad para Producción

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` única y segura
- [ ] `ALLOWED_HOSTS` configurados correctamente
- [ ] Credenciales de producción activas
- [ ] SSL/HTTPS habilitado
- [ ] Base de datos PostgreSQL configurada
- [ ] Archivos estáticos recopilados
- [ ] Modelos ML entrenados y funcionales

### Comando de Verificación

```bash
python manage.py check --deploy
```

## 📋 Pasos para Despliegue en Railway

### 1. Preparar Base de Datos

```bash
# Backup local si es necesario
cp db.sqlite3 db_backup.sqlite3

# O exportar datos
python manage.py dumpdata > data_backup.json
```

### 2. Configurar Railway

- Crear proyecto en Railway
- Configurar PostgreSQL database
- Variables de entorno requeridas:
  ```
  DATABASE_URL=postgresql://...
  SECRET_KEY=tu_secret_key_segura
  DEBUG=False
  ALLOWED_HOSTS=tu-app.up.railway.app
  ```

### 3. Despliegue Automático

Railway detectará los archivos de configuración y ejecutará:

- Instalación de dependencias
- Migraciones de base de datos
- Recopilación de archivos estáticos
- Entrenamiento de modelos ML (opcional)

## 🆘 Solución de Problemas

### Error de Base de Datos

```bash
# Verificar conexión
python manage.py dbshell

# Ejecutar migraciones
python manage.py migrate

# Verificar estado
python manage.py showmigrations
```

### Error de Credenciales

```bash
# Test Firebase
python -c "import firebase_admin; print('Firebase OK')"

# Test Stripe
python -c "import stripe; print('Stripe OK')"
```

### Error de Modelos ML

```bash
# Reentrenar
python train_ml_models.py

# Verificar archivos
ls -la ml_models/
```

## 📊 Monitoreo y Logs

### Railway

```bash
railway logs
```

### Heroku

```bash
heroku logs -a tu-app-name
```

### Health Check Endpoint

```bash
curl https://tu-dominio.com/api/health/
```

## 🔄 Actualizaciones

### Código

```bash
git add .
git commit -m "feat: Nueva funcionalidad"
git push origin main
```

### Dependencias

```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: Actualizar dependencias"
git push origin main
```

## 📁 Archivos de Configuración Incluidos

- ✅ `.env.production.template` - Template de variables de entorno
- ✅ `railway.toml` - Configuración para Railway
- ✅ `Procfile` - Configuración para Heroku
- ✅ `runtime.txt` - Versión de Python
- ✅ `deploy_production.sh` - Script de despliegue
- ✅ `create_production_credentials.py` - Generador de credenciales
- ✅ `train_ml_models.py` - Entrenador de modelos ML
- ✅ `firebase-credentials-production.json` - Credenciales de Firebase
- ✅ `google-cloud-credentials-production.json` - Credenciales de GCP

## 🎯 Checklist Final

- [ ] Repositorio conectado a plataforma de despliegue
- [ ] Variables de entorno configuradas con valores reales
- [ ] Credenciales de producción codificadas en base64
- [ ] Base de datos PostgreSQL funcionando
- [ ] Modelos ML entrenados y guardados
- [ ] Archivos estáticos recopilados
- [ ] HTTPS/SSL habilitado
- [ ] Tests ejecutados en entorno de producción
- [ ] Monitoreo configurado
- [ ] Backup de base de datos realizado

---

¡Tu aplicación backend está completamente preparada para producción! 🚀

**URL del repositorio**: https://github.com/hebertsb/Backend_Parcial2

# Otras variables necesarias

````

### 3. Desplegar Código

```bash
# Subir código a Git y conectar con Railway
git add .
git commit -m "Ready for production"
git push origin main
````

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
