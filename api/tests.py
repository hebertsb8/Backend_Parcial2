from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token


class UserProfileTestCase(APITestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpassword123'
        )
        # Crear token de autenticación
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_change_password_success(self):
        """Test cambio de contraseña exitoso"""
        url = reverse('change-password')
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Contraseña cambiada exitosamente. Por favor, inicia sesión nuevamente.')

        # Verificar que la contraseña se cambió
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))

        # Verificar que el token fue invalidado
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())

    def test_change_password_wrong_old_password(self):
        """Test cambio de contraseña con contraseña antigua incorrecta"""
        url = reverse('change-password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'La contraseña actual es incorrecta')

    def test_change_password_passwords_not_match(self):
        """Test cambio de contraseña con contraseñas que no coinciden"""
        url = reverse('change-password')
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'differentpassword'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'La nueva contraseña y la confirmación no coinciden')

    def test_change_password_too_short(self):
        """Test cambio de contraseña con contraseña demasiado corta"""
        url = reverse('change-password')
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'short',
            'confirm_password': 'short'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'La nueva contraseña debe tener al menos 8 caracteres')

    def test_change_password_user_url_success(self):
        """Test cambio de contraseña usando la URL /api/user/change-password/"""
        url = reverse('change-password-user')
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Contraseña cambiada exitosamente. Por favor, inicia sesión nuevamente.')

        # Verificar que la contraseña se cambió
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))

        # Verificar que el token fue invalidado
        self.assertFalse(Token.objects.filter(key=self.token.key).exists())
