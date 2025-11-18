#!/usr/bin/env python3
"""
Script para generar archivos de credenciales codificados en base64 para producción.
Ejecutar: python create_production_credentials.py
"""

import base64
import json
import os
from pathlib import Path

def create_firebase_credentials():
    """Crear archivo de credenciales de Firebase codificado en base64"""

    # Credenciales de Firebase (reemplaza con tus valores reales de producción)
    firebase_credentials = {
        "type": "service_account",
        "project_id": "your-production-project",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40your-project.iam.gserviceaccount.com"
    }

    # Codificar en base64
    credentials_json = json.dumps(firebase_credentials, indent=2)
    encoded_credentials = base64.b64encode(credentials_json.encode('utf-8')).decode('utf-8')

    # Crear archivo
    output_file = Path(__file__).parent / 'firebase-credentials-production.json'
    with open(output_file, 'w') as f:
        f.write(credentials_json)

    print(f"✅ Archivo de credenciales de Firebase creado: {output_file}")
    print(f"🔐 Credenciales codificadas en base64: {encoded_credentials[:50]}...")

    return encoded_credentials

def create_google_cloud_credentials():
    """Crear archivo de credenciales de Google Cloud codificado en base64"""

    # Credenciales de Google Cloud (reemplaza con tus valores reales)
    gcp_credentials = {
        "type": "service_account",
        "project_id": "your-gcp-project",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }

    # Codificar en base64
    credentials_json = json.dumps(gcp_credentials, indent=2)
    encoded_credentials = base64.b64encode(credentials_json.encode('utf-8')).decode('utf-8')

    # Crear archivo
    output_file = Path(__file__).parent / 'google-cloud-credentials-production.json'
    with open(output_file, 'w') as f:
        f.write(credentials_json)

    print(f"✅ Archivo de credenciales de Google Cloud creado: {output_file}")
    print(f"🔐 Credenciales codificadas en base64: {encoded_credentials[:50]}...")

    return encoded_credentials

def create_ml_training_config():
    """Crear configuración para entrenamiento de modelos ML"""

    ml_config = {
        "training": {
            "enabled": True,
            "auto_retrain": True,
            "retrain_interval_days": 7,
            "min_samples_for_training": 100,
            "test_size": 0.2,
            "random_state": 42
        },
        "models": {
            "sales_predictor": {
                "type": "linear_regression",
                "features": ["month", "day_of_week", "season", "product_category"],
                "target": "sales_amount"
            },
            "product_recommender": {
                "type": "collaborative_filtering",
                "similarity_metric": "cosine",
                "min_ratings_per_user": 5
            }
        },
        "data_sources": {
            "historical_sales": "./ml_models/training_data/historical_sales.csv",
            "product_data": "./ml_models/training_data/products.csv",
            "user_behavior": "./ml_models/training_data/user_behavior.csv"
        },
        "model_paths": {
            "sales_model": "./ml_models/sales_model.pkl",
            "recommender_model": "./ml_models/recommender_model.pkl",
            "scaler": "./ml_models/scaler.pkl"
        }
    }

    # Crear archivo de configuración
    config_file = Path(__file__).parent / 'ml_models' / 'training_config.json'
    config_file.parent.mkdir(exist_ok=True)

    with open(config_file, 'w') as f:
        json.dump(ml_config, f, indent=2)

    print(f"✅ Archivo de configuración ML creado: {config_file}")
    return ml_config

def create_production_env_template():
    """Crear template de variables de entorno para producción"""

    env_template = """
# =============================================================================
# TEMPLATE DE VARIABLES DE ENTORNO PARA PRODUCCIÓN
# Copia este contenido a tu plataforma de despliegue (Railway, Render, etc.)
# =============================================================================

# Django Configuration
SECRET_KEY=tu_clave_secreta_unica_para_produccion_aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,tu-app.onrender.com,*

# CORS Configuration
CORS_ALLOWED_ORIGINS=https://tu-frontend.com,https://tu-app.vercel.app

# Database (PostgreSQL - Railway)
DATABASE_URL=postgresql://postgres:cYpvNcrPVGUMNXKVgkVxeJfEkPJHPbFq@nozomi.proxy.rlwy.net:40214/railway

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# Stripe (Production Keys)
STRIPE_PUBLIC_KEY=pk_live_tu_clave_publica_de_stripe
STRIPE_SECRET_KEY=sk_live_tu_clave_secreta_de_stripe
STRIPE_WEBHOOK_SECRET=whsec_tu_webhook_secret_de_stripe

# Firebase Credentials (Base64 encoded)
FIREBASE_CREDENTIALS_BASE64=tu_credenciales_firebase_codificadas_en_base64
FIREBASE_PUBLIC_API_KEY=tu_api_key_publica_firebase
FIREBASE_AUTH_DOMAIN=tu-proyecto.firebaseapp.com
FIREBASE_PROJECT_ID=tu-project-id
FIREBASE_STORAGE_BUCKET=tu-proyecto.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=tu_sender_id

# Google Cloud Credentials (Base64 encoded)
GOOGLE_CLOUD_CREDENTIALS_BASE64=tu_credenciales_gcp_codificadas_en_base64

# Cache (Redis - opcional)
REDIS_URL=redis://localhost:6379/1

# ML Configuration
ENABLE_ML_TRAINING=True
ML_MODEL_PATH=./ml_models/

# Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
"""

    template_file = Path(__file__).parent / '.env.production.template'
    with open(template_file, 'w') as f:
        f.write(env_template.strip())

    print(f"✅ Template de variables de entorno creado: {template_file}")
    return env_template

def main():
    """Función principal"""
    print("🚀 Generando archivos de credenciales para producción...\n")

    # Crear directorios necesarios
    Path("ml_models").mkdir(exist_ok=True)
    Path("ml_models/training_data").mkdir(exist_ok=True)

    # Generar credenciales
    firebase_b64 = create_firebase_credentials()
    gcp_b64 = create_google_cloud_credentials()

    # Generar configuración ML
    ml_config = create_ml_training_config()

    # Crear template de .env
    env_template = create_production_env_template()

    print("\n" + "="*60)
    print("📋 RESUMEN - Archivos creados para producción:")
    print("="*60)
    print("✅ firebase-credentials-production.json")
    print("✅ google-cloud-credentials-production.json")
    print("✅ ml_models/training_config.json")
    print("✅ .env.production.template")
    print()
    print("🔐 Credenciales codificadas en base64:")
    print(f"   Firebase: {firebase_b64[:50]}...")
    print(f"   GCP: {gcp_b64[:50]}...")
    print()
    print("📝 Próximos pasos:")
    print("1. Reemplaza las credenciales de ejemplo con tus valores reales")
    print("2. Codifica tus credenciales reales en base64")
    print("3. Actualiza las variables de entorno en tu plataforma de despliegue")
    print("4. Ejecuta las migraciones: python manage.py migrate")
    print("5. Entrena los modelos ML: python manage.py train_ml_models")
    print("="*60)

if __name__ == "__main__":
    main()