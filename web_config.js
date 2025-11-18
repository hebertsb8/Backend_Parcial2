# Configuración para conectar Frontend Web con Django Backend
# Archivo: web_config.js (crear en el proyecto web)

const API_CONFIG = {
  // Configuración de base URL según el entorno
  baseURL: process.env.NODE_ENV === 'production'
    ? 'https://tu-backend.com'
    : 'http://localhost:8000', // Para desarrollo local

  // Para emuladores/dispositivos (si usas web móvil)
  baseURLMobile: 'http://10.0.2.2:8000', // Android emulator
  baseURLEmulator: 'http://localhost:8000', // iOS simulator

  // Endpoints principales
  endpoints: {
    auth: {
      login: '/api/auth/login/',
      register: '/api/auth/register/',
      logout: '/api/auth/logout/',
      profile: '/api/auth/profile/'
    },
    products: {
      list: '/api/products/',
      detail: '/api/products/{id}/',
      categories: '/api/products/categories/',
      search: '/api/products/search/'
    },
    sales: {
      cart: '/api/sales/cart/',
      orders: '/api/sales/orders/',
      checkout: '/api/sales/checkout/'
    },
    notifications: {
      registerToken: '/api/notifications/device-tokens/register/',
      send: '/api/notifications/notifications/send/',
      list: '/api/notifications/notifications/',
      markRead: '/api/notifications/notifications/{id}/mark_read/',
      unreadCount: '/api/notifications/notifications/unread_count/',
      preferences: '/api/notifications/preferences/my/',
      // Nuevos endpoints para campañas (solo admin)
      campaigns: {
        list: '/api/notifications/campaigns/',
        create: '/api/notifications/campaigns/',
        detail: '/api/notifications/campaigns/{id}/',
        send: '/api/notifications/campaigns/{id}/send_campaign/',
        failed: '/api/notifications/campaigns/{id}/failed_notifications/',
        stats: '/api/notifications/campaigns/{id}/campaign_stats/',
        fcmUsers: '/api/notifications/notifications/fcm_users/' // Para obtener usuarios con tokens
      }
    }
  },

  // Configuración de Firebase (Web Push)
  firebase: {
    apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
    authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
    storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.REACT_APP_FIREBASE_APP_ID,
    vapidKey: process.env.REACT_APP_FIREBASE_VAPID_KEY
  },

  // Configuración de timeouts y constantes
  timeout: 30000, // 30 segundos
  retryAttempts: 3,

  // Tipos de notificación soportados
  notificationTypes: {
    CUSTOM: 'CUSTOM',
    PROMOTIONAL: 'PROMOTIONAL',
    URGENTE: 'URGENTE',
    CAMPAÑA_MARKETING: 'CAMPAÑA_MARKETING',
    ACTUALIZACION_SISTEMA: 'ACTUALIZACION_SISTEMA',
    INFORMATIVA: 'INFORMATIVA'
  },

  // Plataformas soportadas
  platforms: {
    WEB: 'WEB',
    ANDROID: 'ANDROID',
    IOS: 'IOS'
  }
};

export default API_CONFIG;