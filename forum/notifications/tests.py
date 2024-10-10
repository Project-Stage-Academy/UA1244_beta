from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from startups.models import Startup
from investors.models import Investor
from projects.models import Project
from notifications.models import Notification


class NotificationTestCase(TestCase):
    """
    Test case class to test notification functionality when investors interact with projects.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data that will be used for all test cases in this suite.
        """

        # Create a startup user and an investor user
        cls.startup_user = User.objects.create_user(
            email='startup@example.com',
            password='password123',
            username='startup_user',
            first_name='Startup',
            last_name='User',
            is_active=True
        )

        cls.investor_user = User.objects.create_user(
            email='investor@example.com',
            password='password123',
            username='investor_user',
            first_name='Investor',
            last_name='User',
            is_active=True
        )

        # Create a startup (Онови це відповідно до того, які поля насправді є у моделі Startup)
        cls.startup = Startup.objects.create(
            user=cls.startup_user,  # Якщо є зв'язок із користувачем
            # Використовуй реальні поля зі своєї моделі Startup
        )

        # Create an investor (теж використовуй правильні поля для моделі Investor)
        cls.investor = Investor.objects.create(
            user=cls.investor_user,  # Якщо є зв'язок із користувачем
            # Використовуй реальні поля зі своєї моделі Investor
        )

        # Create a project associated with the startup
        cls.project = Project.objects.create(
            startup=cls.startup,
            title='Test Project',
            description='This is a test project.',
            required_amount=100000,
            status='open'
        )

        # Generate JWT tokens for the users
        cls.startup_token = str(RefreshToken.for_user(cls.startup_user).access_token)
        cls.investor_token = str(RefreshToken.for_user(cls.investor_user).access_token)

        # Set up URLs for testing
        cls.follow_url = reverse('projects:follow_project', args=[cls.project.id])
        cls.unfollow_url = reverse('projects:unfollow_project', args=[cls.project.id])
        cls.notifications_url = reverse('notifications:notification_list')
        cls.notification_settings_url = reverse('notifications:notification_settings')

    def setUp(self):
        """
        Set up that runs before each individual test case.
        """
        self.client = APIClient()

    def authenticate(self, token):
        """
        Helper method to authenticate a user using JWT token.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_follow_project_creates_notification(self):
        """
        Test that following a project creates a notification.
        """
        self.authenticate(self.investor_token)

        # Send a POST request to follow the project
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, 201)

        # Verify that a notification was created
        notification_exists = Notification.objects.filter(
            project=self.project,
            investor=self.investor,
            startup=self.project.startup,
            trigger='project_follow'
        ).exists()

        self.assertTrue(notification_exists)

    def test_unfollow_project_creates_notification(self):
        """
        Test that unfollowing a project creates a notification.
        """
        self.authenticate(self.investor_token)

        # Follow the project first
        self.client.post(self.follow_url)

        # Now unfollow the project
        response = self.client.post(self.unfollow_url)
        self.assertEqual(response.status_code, 200)

        # Verify that another notification was created for unfollow
        notification_exists = Notification.objects.filter(
            project=self.project,
            investor=self.investor,
            startup=self.project.startup,
            trigger='project_unfollow'
        ).exists()

        self.assertTrue(notification_exists)

    def test_turn_off_email_notifications(self):
        """
        Test that email notifications can be turned off.
        """
        self.authenticate(self.startup_token)

        # Send a PUT request to update notification settings
        data = {
            'email_project_updates': False
        }
        response = self.client.put(self.notification_settings_url, data, format='json')
        self.assertEqual(response.status_code, 200)

        # Check that the email notification setting was turned off
        self.assertFalse(response.data['email_project_updates'])

    def test_turn_off_push_notifications(self):
        """
        Test that push notifications can be turned off.
        """
        self.authenticate(self.startup_token)

        # Send a PUT request to update notification settings
        data = {
            'push_project_updates': False
        }
        response = self.client.put(self.notification_settings_url, data, format='json')
        self.assertEqual(response.status_code, 200)

        # Check that the push notification setting was turned off
        self.assertFalse(response.data['push_project_updates'])

    def test_unauthorized_user_cannot_follow_project(self):
        """
        Test that an unauthorized user cannot follow a project.
        """
        # Try to follow the project without authentication
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, 401)  # Expecting an unauthorized error

    def test_unauthorized_user_cannot_unfollow_project(self):
        """
        Test that an unauthorized user cannot unfollow a project.
        """
        # Try to unfollow the project without authentication
        response = self.client.post(self.unfollow_url)
        self.assertEqual(response.status_code, 401)  # Expecting an unauthorized error
