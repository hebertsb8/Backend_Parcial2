# FLUJO DE CONFIGURACIÓN - ARQUITECTURA HÍBRIDA

## 📋 ¿Dónde van los datos de Firebase Console?

### ❌ NO hay .env en el Frontend

- El frontend NO tiene variables de entorno
- El frontend NO tiene credenciales de Firebase
- El frontend obtiene la configuración del backend

### ✅ SÓLO hay .env en el Backend

```
📁 TU_PROYECTO/
├── 📁 backend/          ← Django (tiene .env)
│   ├── .env            ← ✅ CONFIGURACIÓN AQUÍ
│   ├── settings.py
│   └── ...
└── 📁 frontend/         ← React/Next.js (NO tiene .env)
    ├── components/
    └── ...
```

## 🔄 Flujo de Funcionamiento

```
1. Firebase Console → Copias valores → .env (Backend)
2. Frontend → Pide config → GET /api/firebase_config/
3. Backend → Da config segura → Frontend
4. Frontend → Usa config → Obtiene token FCM real
5. Frontend → Registra token → Backend valida y guarda
```

## 🎯 Respuesta a tu pregunta:

**Los datos de Firebase Console van en el BACKEND (.env), NO en el frontend.**

El frontend obtiene esa información de forma segura a través del endpoint que creamos.
