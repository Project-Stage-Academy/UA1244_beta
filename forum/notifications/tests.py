"""
Test cases for the Notifications application.

This module includes unit tests for creating, updating, retrieving, and deleting notifications, 
as well as tests for notification preferences and permissions.
"""

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from investors.models import Investor
from notifications.consumers import NotificationConsumer
from notifications.models import Notification, StartupNotificationPreferences
from notifications.tasks import create_notification_task, trigger_notification_task
from notifications.utils import trigger_notification, notify_user
from projects.models import Project
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from startups.models import Startup
from users.models import Role, User
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

    def test_create_notification_prefs(self):
        """
        Test creating notification preferences for a user.
        Verifies that the preferences are created with a 201 Created response.
        """
        url = reverse('notificationpreferences-list')
        data = {'email_project_updates': False, 'push_project_updates': True}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_notification_prefs(self):
        """
        Test listing notification preferences for a user.
        Verifies that the preferences list is retrieved successfully with a 200 OK response.
        """
        url = reverse('notificationpreferences-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_notification_task(self):
        """
        Test creating a notification through the create_notification_task.
        Ensures that a notification for 'investor_follow' is created and exists in the database.
        """
        create_notification_task("investor", self.investor.investor_id, "investor_follow", "Followed a startup", initiator="system")
        notification_exists = Notification.objects.filter(investor=self.investor, trigger="investor_follow").exists()
        self.assertTrue(notification_exists)

    def test_trigger_notification_task(self):
        """
        Test triggering a notification using trigger_notification_task.
        Confirms that the task completes without returning a result.
        """
        result = trigger_notification_task(self.investor.investor_id, self.startup.startup_id, self.project.project_id, "project_follow")
        self.assertIsNone(result)

    def test_trigger_notification_utility(self):
        """
        Test triggering a notification using the trigger_notification utility function.
        Verifies that a notification is created and stored for the specified investor and project.
        """
        trigger_notification(self.investor, self.startup, self.project, "project_follow")
        notification_exists = Notification.objects.filter(investor=self.investor, trigger="project_follow").exists()
        self.assertTrue(notification_exists)

    def test_mark_as_read_non_existent_notification(self):
        """
        Test marking a non-existent notification as read.
        Verifies that a 404 Not Found status is returned.
        """
        non_existent_notification_id = 9999
        url = reverse('mark-as-read', kwargs={'notification_id': non_existent_notification_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Notification not found')

    def test_invalid_data_in_trigger_notification(self):
        """
        Test sending invalid data to trigger a notification.
        Verifies that a 400 Bad Request status is returned.
        """
        url = reverse('notification-trigger')
        data = {
            "investor_id": "invalid_id",  # invalid ID format
            "startup_id": self.startup.startup_id,
            "project_id": self.project.project_id,
            "trigger_type": "project_follow"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('investor_id', response.data)

    def test_create_notification_preference_with_invalid_role(self):
        """
        Test creating notification preferences with a user who lacks investor or startup roles.
        Verifies that a 403 Forbidden status is returned.
        """
        user_without_roles = User.objects.create_user(
            username='no_role_user',
            email='noroleuser@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=user_without_roles)
        url = reverse('notificationpreferences-list')
        response = self.client.post(url, {'email_project_updates': True})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_notification_as_read_twice(self):
        """
        Test marking a notification as read twice.
        Verifies that the notification remains marked as read.
        """
        url = reverse('mark-as-read', kwargs={'notification_id': self.notification.pk})
        # Mark as read the first time
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Attempt to mark as read a second time
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)

    def test_list_notification_prefs(self):
        """
        Test listing notification preferences for the user.
        Verifies successful retrieval of preferences.
        """
        url = reverse('notificationpreferences-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NotificationConsumerTestCase(TestCase):
    """
    TestCase for NotificationConsumer WebSocket functionality, which tests
    the ability of authenticated users to receive real-time notifications.
    """
    async def test_websocket_connection_and_notification(self):
        """
        Test WebSocket connection and reception of a notification message.
        Ensures that an authenticated user can connect to the WebSocket,
        receive a notification, and disconnect successfully.
        """
        user = await sync_to_async(User.objects.create_user)(
            username='ws_user', email='ws_user@example.com', password='password123'
        )

        # Initialize WebSocket communicator for NotificationConsumer
        communicator = WebsocketCommunicator(NotificationConsumer.as_asgi(), "/ws/notifications/")
        communicator.scope['user'] = user
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send test message to the WebSocket group
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f'notifications_{user.pk}',
            {
                'type': 'send_notification',
                'message': 'Test Notification'
            }
        )

        # Receive the message from WebSocket
        response = await communicator.receive_json_from()
        self.assertEqual(response, {'message': 'Test Notification'})

        # Disconnect the WebSocket
        await communicator.disconnect()


class NotificationTasksTestCase(TestCase):
    """
    TestCase for notification-related tasks, ensuring notifications
    can be created and triggered through Celery tasks.
    """
    def setUp(self):
        """
        Set up test objects for Celery tasks, including a user, an investor,
        a startup, and a project, to verify task-based notifications.
        """
        self.user = User.objects.create_user(username='task_user', email='task_user@test.com', password='password123')
        self.investor = Investor.objects.create(user=self.user)
        self.startup = Startup.objects.create(user=self.user, company_name='Startup Test')
        self.project = Project.objects.create(startup=self.startup, title='Test Project', required_amount=10000.00)

    def test_create_notification_task_project(self):
        """
        Test that a notification is created for a project update using
        the create_notification_task Celery task.
        """
        create_notification_task("project", self.project.project_id, "project_update", "Project was updated")
        notification_exists = Notification.objects.filter(project=self.project, trigger="project_update").exists()
        self.assertTrue(notification_exists)

    def test_trigger_notification_task(self):
        """
        Test that a triggered notification works as expected using
        the trigger_notification_task Celery task.
        """
        result = trigger_notification_task(
            investor_id=self.investor.investor_id,
            startup_id=self.startup.startup_id,
            project_id=self.project.project_id,
            trigger_type="project_follow"
        )
        self.assertIsNone(result)


class NotificationUtilsTestCase(TestCase):
    """
    TestCase for notification utility functions, validating that notifications
    are created and users are notified according to role permissions.
    """
    def setUp(self):
        """
        Set up a user and related objects for utility tests, including
        an investor, a startup, and a project.
        """
        self.user = User.objects.create_user(username='util_user', email='util_user@test.com', password='password123')
        self.investor = Investor.objects.create(user=self.user)
        self.startup = Startup.objects.create(user=self.user, company_name="Startup Util Test")
        self.project = Project.objects.create(startup=self.startup, title='Test Project', required_amount=10000.00)

    def test_trigger_notification(self):
        """
        Test that a notification is created using the trigger_notification
        utility function for a specified project and startup.
        """
        trigger_notification(investor=None, startup=self.startup, project=self.project, trigger_type="project_update")
        notification_exists = Notification.objects.filter(
            startup=self.startup, project=self.project, trigger="project_update"
        ).exists()
        self.assertTrue(notification_exists)

    def test_notify_user_no_permissions(self):
        """
        Test that a user without appropriate roles cannot receive notifications.
        Verifies that a message is returned indicating lack of permissions.
        """
        new_user = User.objects.create_user(username='no_role_user', email='ut_user@test.com', password='password123')
        result = notify_user(new_user, "new_follow", "Test Message")
        self.assertEqual(result, "User does not have the required role of investor or startup.")