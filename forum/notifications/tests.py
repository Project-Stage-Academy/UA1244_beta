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

      
        cls.startup = Startup.objects.create(
            user=cls.startup_user,  
           
        )

        
        cls.investor = Investor.objects.create(
            user=cls.investor_user,  
            
        )

        
        cls.project = Project.objects.create(
            startup=cls.startup,
            title='Test Project',
            description='This is a test project.',
            required_amount=100000,
            status='open'
        )

        
        cls.startup_token = str(RefreshToken.for_user(cls.startup_user).access_token)
        cls.investor_token = str(RefreshToken.for_user(cls.investor_user).access_token)

       
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

        
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, 201)

        
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

       
        self.client.post(self.follow_url)

        
        response = self.client.post(self.unfollow_url)
        self.assertEqual(response.status_code, 200)

        
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

        
        data = {
            'email_project_updates': False
        }
        response = self.client.put(self.notification_settings_url, data, format='json')
        self.assertEqual(response.status_code, 200)

        
        self.assertFalse(response.data['email_project_updates'])

    def test_turn_off_push_notifications(self):
        """
        Test that push notifications can be turned off.
        """
        self.authenticate(self.startup_token)

        
        data = {
            'push_project_updates': False
        }
        response = self.client.put(self.notification_settings_url, data, format='json')
        self.assertEqual(response.status_code, 200)

       
        self.assertFalse(response.data['push_project_updates'])

    def test_unauthorized_user_cannot_follow_project(self):
        """
        Test that an unauthorized user cannot follow a project.
        """
        
        response = self.client.post(self.follow_url)
        self.assertEqual(response.status_code, 401)  

    def test_unauthorized_user_cannot_unfollow_project(self):
        """
        Test that an unauthorized user cannot unfollow a project.
        """
        
        response = self.client.post(self.unfollow_url)
        self.assertEqual(response.status_code, 401)  
