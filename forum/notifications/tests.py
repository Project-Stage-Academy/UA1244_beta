from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Notification, StartupNotificationPreferences, Investor, Startup, Project
from .serializers import NotificationSerializer, StartupNotificationPrefsSerializer
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
        # Створюємо користувача з email і паролем, додаємо username
        cls.user = User.objects.create_user(
            username='user_test_1',
            email='frent3219@gmail.com',
            password='SecurePassword263!',
            is_active=True
        )

        # Створюємо ролі для інвестора та стартапу
        investor_role = Role.objects.create(name='investor')
        startup_role = Role.objects.create(name='startup')

        # Додаємо ролі до користувача
        cls.user.roles.add(investor_role)
        cls.user.roles.add(startup_role)

        # Створюємо Startup і Investor для цього користувача
        cls.startup = Startup.objects.create(user=cls.user, company_name='Startup A')
        cls.investor = Investor.objects.create(user=cls.user)
        
        # Створюємо проект для стартапу
        cls.project = Project.objects.create(
            startup=cls.startup, 
            title='Project A', 
            description='Description A', 
            required_amount=10000.00
        )
        cls.startup_prefs = StartupNotificationPreferences.objects.create(startup=cls.startup)

        # Створюємо сповіщення з фейковим URL для тестування
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
        self.assertTrue(self.user.roles.filter(name='investor').exists())
        self.assertTrue(self.user.roles.filter(name='startup').exists())
        
    def test_get_notification_preferences_for_startup(self):
        """
        Test the retrieval of notification preferences for a startup.
        Verifies that the preferences are correctly fetched.
        """
        url = reverse('notificationpreferences-detail', kwargs={'pk': self.startup_prefs.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email_project_updates'], True)

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
        
        # Verify that preferences were actually updated
        self.startup_prefs.refresh_from_db()
        self.assertTrue(self.startup_prefs.email_project_updates)
        self.assertFalse(self.startup_prefs.email_startup_updates)

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
            # Створюємо мокове сповіщення, якщо список порожній
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
        
        # Verify that notification was marked as read
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
        This should raise a ValidationError.
        """
        invalid_notification_data = {
            'trigger': 'project_follow',
            'initiator': 'investor'
        }
        with self.assertRaises(ValidationError):
            Notification.objects.create(**invalid_notification_data)

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

    def test_update_notification_preferences_with_invalid_data(self):
        """
        Test trying to update notification preferences with invalid data.
        Should return a 400 Bad Request status.
        """
        url = reverse('notification-prefs-update')
        invalid_data = {
            'email_project_updates': 'invalid_value'
        }
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
