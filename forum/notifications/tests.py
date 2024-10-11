from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Notification, StartupNotificationPreferences, Investor, Startup, Project
from .serializers import NotificationSerializer, StartupNotificationPrefsSerializer
from unittest.mock import patch
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()

class NotificationTests(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        
        # Створення користувача для тестів
        self.user_data = {
            'email': 'frent3219@gmail.com',
            'password': 'SecurePassword263!',
            'is_active': True
        }
        self.user = User.objects.create_user(**self.user_data)
        self.user.save()

        # Логін і отримання токена
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': self.user_data['email'], 
            'password': self.user_data['password']
        })
        
        if response.status_code != status.HTTP_200_OK:
            self.fail(f"Не вдалося отримати токен доступу. Код відповіді: {response.status_code}, дані: {response.data}")

        # Отримання токену
        self.token = response.data.get('access')
        self.refresh_token = response.data.get('refresh')

        if not self.token:
            self.fail("Не вдалося отримати токен доступу із відповіді.")
    
        # Додавання токену до заголовків
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Створення даних для тестів
        self.startup = Startup.objects.create(user=self.user, company_name='Startup A')
        self.investor = Investor.objects.create(user=self.user)
        self.project = Project.objects.create(startup=self.startup, title='Project A', description='Description A', required_amount=10000.00)
        self.startup_prefs = StartupNotificationPreferences.objects.create(startup=self.startup)
        
        # Створення сповіщення
        self.notification = Notification.objects.create(
            investor=self.investor,
            startup=self.startup,
            project=self.project,
            trigger='project_follow',
            initiator='investor',
            redirection_url=f'/projects/{self.project.pk}/' if self.project else ''
        )

    def test_get_notification_preferences_for_startup(self):
        url = reverse('notificationpreferences-detail', kwargs={'pk': self.startup_prefs.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_notification_preferences_for_startup(self):
        url = reverse('notification-prefs-update')
        response = self.client.post(url, {
            'email_project_updates': True,
            'push_project_updates': True,
            'email_startup_updates': False,
            'push_startup_updates': False
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_notifications_list(self):
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Notification.objects.filter(pk=self.notification.pk).exists())
        self.assertEqual(len(response.data), 1)

    def test_mark_notification_as_read(self):
        url = reverse('mark-as-read', kwargs={'notification_id': self.notification.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_notification(self):
        url = reverse('delete-notification', kwargs={'notification_id': self.notification.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notification.objects.filter(pk=self.notification.pk).exists())


class NotificationModelTest(APITestCase):
    """
    Test cases for Notification model functionalities.
    """

    def setUp(self):
        """
        Set up executed before each test case.
        """
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.startup = Startup.objects.create(user=self.user, company_name='Test Startup')
        self.startup_prefs = StartupNotificationPreferences.objects.create(startup=self.startup)
        self.investor = Investor.objects.create(user=self.user)
        self.project = Project.objects.create(startup=self.startup, title='Project B', description='Description B', required_amount=15000.00)
        self.notification = Notification.objects.create(
            investor=self.investor,
            startup=self.startup,
            project=self.project,
            trigger="project_follow",
            redirection_url=f'/projects/{self.project.pk}/' if self.project else ''
        )

    def test_notification_creation(self):
        """
        Test to verify notification creation.
        """
        self.assertEqual(Notification.objects.count(), 1)

    def test_notification_serializer(self):
        """
        Test to verify the Notification serializer.
        """
        serializer = NotificationSerializer(self.notification)
        self.assertIn('trigger', serializer.data)
        self.assertIn('is_read', serializer.data)

    def test_startup_notification_prefs_serializer(self):
        """
        Test to verify the StartupNotificationPreferences serializer.
        """
        serializer = StartupNotificationPrefsSerializer(self.startup_prefs)
        self.assertIn('email_project_updates', serializer.data)
        self.assertTrue(serializer.data['email_project_updates'])
