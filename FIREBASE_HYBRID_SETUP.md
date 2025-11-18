# Configuración de Firebase - Solución Híbrida Segura

## 📋 ¿Dónde obtener las credenciales?

### 🔐 Credenciales Sensibles (Archivo JSON)

- **Ubicación**: Firebase Console → Project Settings → Service Accounts → Generate Private Key
- **Archivo**: `firebase-credentials.json` (descárgalo y colócalo en la raíz del proyecto)
- **Variable**: `FIREBASE_CREDENTIALS_PATH=/ruta/a/firebase-credentials.json`
- **Uso**: Solo backend (Admin SDK)

### 🌐 Credenciales Públicas (Variables de Entorno)

- **Ubicación**: Firebase Console → Project Settings → General → Your apps → Web app
- **Cómo obtenerlas**:

#### Paso 1: Ir a Firebase Console

1. Ve a https://console.firebase.google.com/
2. Selecciona tu proyecto
3. Ve a Project Settings (⚙️)

#### Paso 2: Obtener configuración web

1. En la pestaña "General", ve a "Your apps"
2. Si no tienes app web, crea una: "Add app" → "</>" (Web)
3. Copia la configuración que aparece

#### Paso 3: Variables de entorno (.env)

```bash
# Configuración pública (de Firebase Console - General - Your apps - Web app)
FIREBASE_PUBLIC_API_KEY=AIzaSyD... (apiKey)
FIREBASE_AUTH_DOMAIN=tu-proyecto.firebaseapp.com (authDomain)
FIREBASE_PROJECT_ID=tu-proyecto-id (projectId)
FIREBASE_STORAGE_BUCKET=tu-proyecto.appspot.com (storageBucket)
FIREBASE_MESSAGING_SENDER_ID=123456789 (messagingSenderId)
FIREBASE_APP_ID=1:123456789:web:abcdef123456 (appId)

# Para notificaciones web push (opcional - generar en Cloud Messaging)
FIREBASE_VAPID_KEY=tu_vapid_key_para_web_push
```

### 📱 Para Apps Móviles (Android/iOS)

Si también tienes apps móviles, registra cada plataforma en Firebase Console y obtén sus respectivos app IDs.

## 🔄 Flujo de Funcionamiento

1. **Frontend** → `GET /api/notifications/device-tokens/firebase_config/`
2. **Backend** → Retorna configuración pública desde variables de entorno
3. **Frontend** → Usa config para inicializar Firebase SDK
4. **Frontend** → Obtiene token FCM real
5. **Frontend** → `POST /api/notifications/device-tokens/register/` con token
6. **Backend** → Valida token enviando notificación de prueba
7. **Backend** → Guarda token si es válido
8. **Admin** → `GET /api/notifications/notifications/fcm_users/` ve usuarios

## ✅ Beneficios de Seguridad

- ✅ **Credenciales sensibles** permanecen solo en backend
- ✅ **Configuración pública** se comparte controladamente
- ✅ **Validación automática** de tokens antes de guardar
- ✅ **Mayor control** sobre qué configuración se expone

## 🔗 Endpoints Disponibles

- `GET /api/notifications/device-tokens/firebase_config/` - Obtener config para frontend
- `POST /api/notifications/device-tokens/register/` - Registrar token FCM (con validación)
- `GET /api/notifications/notifications/fcm_users/` - Listar usuarios con FCM (admin)
