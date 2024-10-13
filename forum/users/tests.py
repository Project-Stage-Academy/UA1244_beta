from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Role, User

class ChangeActiveRoleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        self.startup_role = Role.objects.create(name='startup')
        self.investor_role = Role.objects.create(name='investor')
        self.unassigned_role = Role.objects.create(name='unassigned')
        self.client.login(username='testuser', password='testpass')

    def test_change_role_to_investor(self):
        url = reverse('change-role')
        data = {'role_name': 'investor'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.active_role.name, 'investor')

    def test_invalid_role(self):
        url = reverse('change-role')
        data = {'role_name': 'nonexistent_role'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Role nonexistent_role does not exist.", response.data['error'])