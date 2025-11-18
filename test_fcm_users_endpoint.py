#!/usr/bin/env python3
"""
Script para probar el endpoint de usuarios FCM
Ejecutar: python test_fcm_users_endpoint.py
"""

import requests
import json

def test_fcm_users_endpoint():
    """Probar el endpoint de usuarios con FCM tokens"""

    print("🧪 Probando endpoint: /api/notifications/notifications/fcm_users/")
    print("=" * 60)

    try:
        # Obtener token de admin
        login_response = requests.post(
            'http://localhost:8000/api/login/',
            json={'username': 'admin', 'password': 'admin123'}
        )

        if login_response.status_code != 200:
            print(f"❌ Error obteniendo token: {login_response.status_code}")
            print(login_response.text)
            return

        token = login_response.json().get('token')
        print(f"✅ Token obtenido: {token[:20]}...")

        # Probar endpoint de usuarios FCM
        headers = {'Authorization': f'Token {token}'}
        fcm_response = requests.get(
            'http://localhost:8000/api/notifications/notifications/fcm_users/',
            headers=headers
        )

        print(f"📡 Status code: {fcm_response.status_code}")

        if fcm_response.status_code == 200:
            data = fcm_response.json()
            print("✅ Endpoint funciona correctamente")
            print(f"👥 Usuarios con FCM tokens: {data['count']}")

            for user in data['users']:
                print(f"  👤 {user['username']} ({user['role']})")
                print(f"     📧 {user['email']}")
                print(f"     📱 Tokens: {user['tokens_count']}")
                for token_info in user['fcm_tokens']:
                    print(f"        • {token_info['platform']} - {token_info['device_name']}")
                print()
        else:
            print("❌ Error en la respuesta:")
            print(fcm_response.text)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {str(e)}")
        print("💡 Asegúrate de que el servidor esté corriendo con:")
        print("   python manage.py runserver 0.0.0.0:8000")

    print("=" * 60)

if __name__ == "__main__":
    test_fcm_users_endpoint()