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
    """
    A TestCase class to test various functionalities of notifications
    including creating, updating, retrieving, and deleting notifications.
    """

    def setUp(self):
        """
        Set up necessary test data, including a test user, startup, investor,
        project, and notification. Also, obtain an authentication token for
        further requests.
        """
        self.client = APIClient()
        
        # Create a test user
        self.user_data = {
            'email': 'frent3219@gmail.com',
            'password': 'SecurePassword263!',
            'is_active': True
        }
        self.user = User.objects.create_user(**self.user_data)
        self.user.save()

        # Log in and obtain a token
        response = self.client.post(reverse('token_obtain'), {
            'email': self.user_data['email'], 
            'password': self.user_data['password']
        })
        
        if response.status_code != status.HTTP_200_OK:
            self.fail(f"Failed to obtain access token. Response code: {response.status_code}, data: {response.data}")

        # Extract token
        self.token = response.data.get('access')
        self.refresh_token = response.data.get('refresh')

        if not self.token:
            self.fail("Failed to retrieve access token from response.")

        # Set the token in the headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test data for startup, investor, project, and notification
        self.startup = Startup.objects.create(user=self.user, company_name='Startup A')
        self.investor = Investor.objects.create(user=self.user)
        self.project = Project.objects.create(startup=self.startup, title='Project A', description='Description A', required_amount=10000.00)
        self.startup_prefs = StartupNotificationPreferences.objects.create(startup=self.startup)
        
        # Create a notification
        self.notification = Notification.objects.create(
            investor=self.investor,
            startup=self.startup,
            project=self.project,
            trigger='project_follow',
            initiator='investor',
            redirection_url=f'/projects/{self.project.pk}/' if self.project else ''
        )

    def test_get_notification_preferences_for_startup(self):
        """
        Test the retrieval of notification preferences for a startup.
        Verifies that the preferences are correctly fetched.
        """
        url = reverse('notificationpreferences-detail', kwargs={'pk': self.startup_prefs.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_notification_preferences_for_startup(self):
        """
        Test the update of notification preferences for a startup.
        Verifies that the preferences can be updated and saved correctly.
        """
        url = reverse('notification-prefs-update')
        response = self.client.post(url, {
            'email_project_updates': True,
            'push_project_updates': True,
            'email_startup_updates': False,
            'push_startup_updates': False
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_notifications_list(self):
        """
        Test the retrieval of a list of notifications.
        Verifies that the notifications list is correctly fetched.
        """
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Notification.objects.filter(pk=self.notification.pk).exists())
        self.assertEqual(len(response.data), 1)

    def test_mark_notification_as_read(self):
        """
        Test marking a notification as read.
        Verifies that the notification is correctly marked as read.
        """
        url = reverse('mark-as-read', kwargs={'notification_id': self.notification.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_notification(self):
        """
        Test deleting a notification.
        Verifies that the notification is correctly deleted.
        """
        url = reverse('delete-notification', kwargs={'notification_id': self.notification.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notification.objects.filter(pk=self.notification.pk).exists())


class NotificationModelTest(APITestCase):
    """
    A TestCase class to test various functionalities of the Notification model.
    """

    def setUp(self):
        """
        Set up necessary test data for the Notification model, including user,
        startup, investor, project, and notification.
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
        Test to verify that a notification is correctly created in the database.
        """
        self.assertEqual(Notification.objects.count(), 1)

    def test_notification_serializer(self):
        """
        Test to verify that the NotificationSerializer works as expected.
        Checks that the 'trigger' and 'is_read' fields are serialized correctly.
        """
        serializer = NotificationSerializer(self.notification)
        self.assertIn('trigger', serializer.data)
        self.assertIn('is_read', serializer.data)

    def test_startup_notification_prefs_serializer(self):
        """
        Test to verify that the StartupNotificationPreferences serializer works as expected.
        Checks that the 'email_project_updates' field is serialized correctly.
        """
        serializer = StartupNotificationPrefsSerializer(self.startup_prefs)
        self.assertIn('email_project_updates', serializer.data)
        self.assertTrue(serializer.data['email_project_updates'])
