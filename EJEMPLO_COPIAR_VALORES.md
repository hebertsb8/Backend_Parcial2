# 📋 EJEMPLO VISUAL: Qué copiar de Firebase Console

## Paso 1: Ve a Firebase Console

🔗 https://console.firebase.google.com/

## Paso 2: Selecciona tu proyecto "smart365"

## Paso 3: Project Settings (⚙️)

## Paso 4: Pestaña "General" → "Your apps" → App Web

## Paso 5: Copia EXACTAMENTE estos valores:

### 📄 Código que verás en Firebase Console:

```javascript
// Configuración de Firebase (SDK)
const firebaseConfig = {
  apiKey: "AIzaSyD1234567890abcdef...", // ← COPIA ESTE
  authDomain: "smart365-88674.firebaseapp.com", // ← COPIA ESTE
  projectId: "smart365-88674", // ← COPIA ESTE
  storageBucket: "smart365-88674.appspot.com", // ← COPIA ESTE
  messagingSenderId: "123456789012", // ← COPIA ESTE
  appId: "1:123456789012:web:abcdef123456789", // ← COPIA ESTE
};
```

### 📝 Pega en tu archivo .env (Backend):

```bash
# Archivo: .env (en la raíz del backend)

# API Key - Copia el valor de apiKey
FIREBASE_PUBLIC_API_KEY=AIzaSyD1234567890abcdef...

# Auth Domain - Copia el valor de authDomain
FIREBASE_AUTH_DOMAIN=smart365-88674.firebaseapp.com

# Project ID - Copia el valor de projectId
FIREBASE_PROJECT_ID=smart365-88674

# Storage Bucket - Copia el valor de storageBucket
FIREBASE_STORAGE_BUCKET=smart365-88674.appspot.com

# Messaging Sender ID - Copia el valor de messagingSenderId
FIREBASE_MESSAGING_SENDER_ID=123456789012

# App ID - Copia el valor de appId
FIREBASE_APP_ID=1:123456789012:web:abcdef123456789
```

## ✅ Verificación:

Después de copiar, ejecuta:

```bash
python check_firebase_config.py
```

Deberías ver: 🎉 ¡Configuración completa!
