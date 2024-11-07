"""
Test cases for the Notifications application.

This module includes unit tests for creating, updating, retrieving, and deleting notifications, 
as well as tests for notification preferences and permissions.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import Notification, StartupNotificationPreferences, Investor, Startup, Project
from users.models import Role

User = get_user_model()

class NotificationTests(APITestCase):
    """
    A TestCase class to test various functionalities of notifications
    including creating, updating, retrieving, and deleting notifications.
    """

    @classmethod
    def setUpTestData(cls):
        investor_role, _ = Role.objects.get_or_create(name='investor')
        startup_role, _ = Role.objects.get_or_create(name='startup')

        # Create a test user
        cls.user = User.objects.create_user(
            username='new_user666',
            email='frent3219@gmail.com',
            password='SecurePassword263!',
            is_active=True
        )
        cls.user.roles.add(investor_role)
        cls.user.roles.add(startup_role)

        # Create a startup and investor instance
        cls.startup = Startup.objects.create(user=cls.user, company_name='Startup A')
        cls.investor = Investor.objects.create(user=cls.user)

        # Create a project
        cls.project = Project.objects.create(
            startup=cls.startup,
            title='Project A',
            description='Description A',
            required_amount=10000.00
        )

        # Create notification preferences for the startup
        cls.startup_prefs = StartupNotificationPreferences.objects.create(startup=cls.startup)

        # Create a notification
        cls.notification = Notification.objects.create(
            investor=cls.investor,
            startup=cls.startup,
            project=cls.project,
            trigger='project_follow',
            initiator='investor',
            redirection_url='http://example.com/fake-url-for-testing/'
        )

    def setUp(self):
        """
        Log in and obtain an authentication token for further requests.
        """
        self.client = APIClient()
        response = self.client.post(reverse('token_obtain'), {
            'email': 'frent3219@gmail.com',
            'password': 'SecurePassword263!'
        })
        self.token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_user_roles(self):
        """
        Test that user has correct roles.
        """
        self.assertTrue(self.user.roles.filter(name='investor').exists())
        self.assertTrue(self.user.roles.filter(name='startup').exists())

    def test_get_notifications_list(self):
        """
        Test the retrieval of a list of notifications.
        Verifies that the notifications list is correctly fetched.
        """
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_notification_as_read(self):
        """
        Test marking a notification as read.
        Verifies that the notification is correctly marked as read.
        """
        url = reverse('mark-as-read', kwargs={'notification_id': self.notification.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_delete_notification(self):
        """
        Test deleting a notification.
        Verifies that the notification is correctly deleted.
        """
        url = reverse('delete-notification', kwargs={'notification_id': self.notification.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notification.objects.filter(pk=self.notification.pk).exists())

    def test_create_notification_without_project_or_startup(self):
        """
        Test creating a notification without a project, startup, or investor.
        This should raise a ValidationError with a specific error message.
        """
        invalid_notification_data = {
            'trigger': 'project_follow',
            'initiator': 'investor'
        }
        with self.assertRaises(ValidationError) as context:
            Notification.objects.create(**invalid_notification_data)

        self.assertIn(
            'At least one of project, startup, or investor must be set.',
            str(context.exception)
        )

    def test_get_notifications_list_without_permission(self):
        """
        Test trying to retrieve a list of notifications for a user without permissions.
        Should return a 403 Forbidden status.
        """
        new_user = User.objects.create_user(
            username='new_user_1',
            email='newuser@test.com',
            password='NewUserPass123!'
        )
        self.client.force_authenticate(user=new_user)
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_non_existent_notification(self):
        """
        Test deleting a non-existent notification.
        Verifies that a 404 Not Found status is returned.
        """
        non_existent_notification_id = 9999  
        url = reverse('delete-notification', kwargs={'notification_id': non_existent_notification_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Notification not found')

    def test_access_notification_with_invalid_role(self):
        """
        Test accessing the notifications endpoint with a user that has an invalid or non-existent role.
        Verifies that access is denied with a 403 Forbidden status.
        """
        user_with_invalid_role = User.objects.create_user(
            username='invalidroleuser',
            email='invalidroleuser@test.com',
            password='InvalidPass123!'
        )
        self.client.force_authenticate(user=user_with_invalid_role)
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')
