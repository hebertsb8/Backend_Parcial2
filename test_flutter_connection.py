#!/usr/bin/env python3
"""
Script de prueba para verificar conexión Flutter-Django
Ejecutar: python test_flutter_connection.py
"""

import requests
import json
import time

def test_connection():
    """Prueba la conexión con el backend desde diferentes IPs"""

    base_urls = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://10.0.2.2:8000",  # IP del emulador Android
    ]

    print("🧪 Probando conexión Flutter-Django Backend")
    print("=" * 50)

    for url in base_urls:
        print(f"\n🌐 Probando: {url}")
        try:
            # Test básico de conectividad
            response = requests.get(f"{url}/api/", timeout=5)
            print(f"   ✅ Conexión básica: {response.status_code}")

            # Test de login (usando credenciales de prueba)
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            login_response = requests.post(f"{url}/api/auth/login/", json=login_data, timeout=5)
            if login_response.status_code == 200:
                token = login_response.json().get('token')
                print(f"   ✅ Login exitoso, token: {token[:20]}...")

                # Test de notificaciones
                headers = {'Authorization': f'Token {token}'}
                notif_response = requests.get(f"{url}/api/notifications/notifications/", headers=headers, timeout=5)
                print(f"   ✅ Notificaciones: {notif_response.status_code}")

            else:
                print(f"   ❌ Login falló: {login_response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {str(e)}")

    print("\n" + "=" * 50)
    print("📱 Configuración para Flutter:")
    print("   • Emulador Android: http://10.0.2.2:8000")
    print("   • Dispositivo físico: http://[IP_LOCAL]:8000")
    print("   • Web: http://localhost:8000")
    print("\n🔧 Asegúrate de que el servidor esté corriendo con:")
    print("   python manage.py runserver 0.0.0.0:8000")

if __name__ == "__main__":
    test_connection()