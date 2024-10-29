from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Notification, StartupNotificationPreferences, Investor, Startup, Project
from users.models import Role
from django.core.exceptions import ValidationError

User = get_user_model()

class NotificationTests(APITestCase):
    """
    A TestCase class to test various functionalities of notifications
    including creating, updating, retrieving, and deleting notifications.
    """

    @classmethod
    def setUpTestData(cls):
        # Ensure the 'unassigned' role exists for users without a specific role.
        unassigned_role, created = Role.objects.get_or_create(name='unassigned')
        investor_role, created = Role.objects.get_or_create(name='investor')
        startup_role, created = Role.objects.get_or_create(name='startup')

        # Create a test user
        cls.user = User.objects.create_user(
            username='new_user666',
            email='frent3219@gmail.com',
            password='SecurePassword263!',
            is_active=True
        )

        assert cls.user is not None, "User not created"

        # Assign investor and startup roles to the user
        cls.user.roles.add(investor_role)
        cls.user.roles.add(startup_role)

        assert cls.user.roles.filter(name='investor').exists(), "Investor role not added"
        assert cls.user.roles.filter(name='startup').exists(), "Startup role not added"

        # Create a startup and investor instance
        cls.startup = Startup.objects.create(user=cls.user, company_name='Startup A')
        cls.investor = Investor.objects.create(user=cls.user)

        assert cls.startup is not None, "Startup not created"
        assert cls.investor is not None, "Investor not created"

        # Create a project
        cls.project = Project.objects.create(
            startup=cls.startup, 
            title='Project A', 
            description='Description A', 
            required_amount=10000.00
        )

        assert cls.project is not None, "Project not created"

        # Create notification preferences for the startup
        cls.startup_prefs = StartupNotificationPreferences.objects.create(startup=cls.startup)

        assert cls.startup_prefs is not None, "Notification preferences not created"

        # Create a notification
        cls.notification = Notification.objects.create(
            investor=cls.investor,
            startup=cls.startup,
            project=cls.project,
            trigger='project_follow',
            initiator='investor',
            redirection_url='http://example.com/fake-url-for-testing/'
        )

        assert cls.notification is not None, "Notification not created"

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
        self.assertIsNotNone(self.token, "Token not obtained")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_user_roles(self):
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
        
        if len(response.data) > 0:
            self.assertEqual(response.data[0]['trigger'], 'project_follow')
        else:
            Notification.objects.create(
                investor=self.investor,
                startup=self.startup,
                project=self.project,
                trigger='project_follow',
                initiator='investor',
                redirection_url='http://example.com/fake-url-for-testing/'
            )
            response = self.client.get(url)
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['trigger'], 'project_follow')

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

        self.assertIn('At least one of project, startup, or investor must be set.', str(context.exception))

    def test_get_notifications_list_without_permission(self):
        """
        Test trying to retrieve a list of notifications for a user without permissions.
        Should return a 403 Forbidden status.
        """
        new_user = User.objects.create_user(username='new_user_1', email='newuser@test.com', password='NewUserPass123!')
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
        
        user_with_invalid_role = User.objects.create_user(username='invalidroleuser', email='invalidroleuser@test.com', password='InvalidPass123!')
        self.client.force_authenticate(user=user_with_invalid_role)

        url = reverse('notification-list')
        response = self.client.get(url)

        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to perform this action.')




