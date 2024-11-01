from django.test import TestCase
from django.urls import reverse
from users.models import Role, User
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch


class RoleTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.unassigned_role = Role.objects.create(name='unassigned')
        cls.startup_role = Role.objects.create(name='startup')
        cls.investor_role = Role.objects.create(name='investor')

    def test_user_creation_with_default_role(self):
        """
        Test to check if a user is automatically assigned the 'unassigned' role.
        """
        user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            username='testuser'
        )
        self.assertEqual(user.active_role.name, 'unassigned', "The user was not assigned the 'unassigned' role by default.")

    def test_change_user_active_role(self):
        """
        Test to verify changing the active role of a user.
        """
        user = User.objects.create_user(
            email='change_role@example.com',
            password='testpass123',
            first_name='Role',
            last_name='Changer',
            username='changer'
        )
        self.assertEqual(user.active_role.name, 'unassigned')

        user.change_active_role('startup')
        self.assertEqual(user.active_role.name, 'startup', "Failed to change the role to 'startup'.")

        user.change_active_role('investor')
        self.assertEqual(user.active_role.name, 'investor', "Failed to change the role to 'investor'.")

    def test_invalid_role_change(self):
        """
        Test to ensure an exception is raised when assigning a non-existent role.
        """
        user = User.objects.create_user(
            email='invalid_role@example.com',
            password='testpass123',
            first_name='Invalid',
            last_name='Role',
            username='invalidrole'
        )
        with self.assertRaises(ValueError, msg="Role 'nonexistent' does not exist."):
            user.change_active_role('nonexistent')

    def test_user_has_default_unassigned_role_after_creation(self):
        """
        Test to check if a user is created with the 'unassigned' role.
        """
        user = User.objects.create_user(
            email='defaultuser@example.com',
            password='password123',
            username='defaultuser',
            first_name='Default',
            last_name='User'
        )
        self.assertIsNotNone(user.active_role)
        self.assertEqual(user.active_role.name, 'unassigned', "The user was not assigned the 'unassigned' role.")

    def test_user_creation_with_explicit_role(self):
        """
        Test to check if a user can be created with an explicit role.
        """
        user = User.objects.create_user(
            email='explicitrole@example.com',
            password='password123',
            username='explicituser',
            first_name='Explicit',
            last_name='User',
            active_role=self.startup_role
        )
        self.assertEqual(user.active_role.name, 'startup', "Failed to assign the 'startup' role to the user during creation.")


class RolePermissionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.unassigned_role = Role.objects.create(name='unassigned')
        cls.startup_role = Role.objects.create(name='startup')
        cls.investor_role = Role.objects.create(name='investor')

        cls.user_investor = User.objects.create_user(
            username='new_user666',
            email='frent3219@gmail.com',
            password='SecurePassword263!',
            is_active=True
        )
        cls.user_investor.active_role = cls.investor_role
        cls.user_investor.save()

        cls.user_startup = User.objects.create_user(
            username='chelakhov176',
            email='frent32@gmail.com',
            password='SecurePassword123!',
            is_active=True
        )
        cls.user_startup.active_role = cls.startup_role
        cls.user_startup.save()

    def authenticate_user(self, email, password):
        """
        Authenticate a user and set JWT token in the request headers.
        """
        url = reverse('token_obtain')
        response = self.client.post(url, {'email': email, 'password': password})
        token = response.data.get('access', None)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return token

    def test_investor_access(self):
        """
        Test access for users with 'investor' role.
        """
        self.authenticate_user('frent3219@gmail.com', 'SecurePassword263!')
        self.assertEqual(self.user_investor.active_role.name, 'investor')
        response = self.client.get(reverse('investor-only'))
        self.assertEqual(response.status_code, 200)

    def test_startup_access(self):
        """
        Test access for users with 'startup' role.
        """
        self.authenticate_user('frent32@gmail.com', 'SecurePassword123!')
        self.assertEqual(self.user_startup.active_role.name, 'startup')
        response = self.client.get(reverse('startup-only'))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_access(self):
        """
        Test access for anonymous users (should be forbidden).
        """
        response = self.client.get(reverse('startup-only'))
        self.assertEqual(response.status_code, 401)



class OAuthTokenObtainPairViewTests(APITestCase):

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    def test_missing_provider_or_code(self, mock_exchange_code_and_get_user_profile):
        """
        Test for missing provider or authorization code.
        """
        response = self.client.post(reverse('token_obtain_oauth'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Provider and code are required"})

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    def test_failed_user_profile_fetch(self, mock_exchange_code_and_get_user_profile):
        """
        Test for handling errors during user profile fetch.
        """
        mock_exchange_code_and_get_user_profile.side_effect = ValueError("Failed to fetch user profile from provider.")

        response = self.client.post(reverse('token_obtain_oauth'), {
            'provider': 'google',
            'code': 'mock_code'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Failed to fetch user profile from provider."})

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    @patch('users.api_view.OAuthTokenObtainPairView.get_or_create_user')
    def test_inactive_user(self, mock_get_or_create_user, mock_exchange_code_and_get_user_profile):
        """
        Ensure inactive users do not receive tokens.
        """
        user = User.objects.create(email='inactiveuser@example.com', is_active=False)
        mock_exchange_code_and_get_user_profile.return_value = ('mock_access_token', {'email': 'inactiveuser@example.com'})
        mock_get_or_create_user.return_value = user

        response = self.client.post(reverse('token_obtain_oauth'), {
            'provider': 'google',
            'code': 'mock_code'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "User account is inactive."})

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    @patch('users.api_view.OAuthTokenObtainPairView.get_or_create_user')
    def test_user_exists(self, mock_get_or_create_user, mock_exchange_code_and_get_user_profile):
        """
        Ensure an existing user is not created again.
        """
        mock_user_data = {'email': 'existinguser@example.com'}
        user = User.objects.create(email='existinguser@example.com', is_active=True)
        mock_exchange_code_and_get_user_profile.return_value = ('mock_access_token', mock_user_data)
        mock_get_or_create_user.return_value = user

        response = self.client.post(reverse('token_obtain_oauth'), {
            'provider': 'google',
            'code': 'mock_code'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    def test_create_new_user(self, mock_exchange_code_and_get_user_profile):
        """
        Ensure a new user is created on first OAuth login.
        """
        mock_user_data = {'email': 'newuser@example.com'}
        mock_exchange_code_and_get_user_profile.return_value = ('mock_access_token', mock_user_data)

        response = self.client.post(reverse('token_obtain_oauth'), {
            'provider': 'google',
            'code': 'mock_code'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    def test_incorrect_auth_code(self, mock_exchange_code_and_get_user_profile):
        """
        Ensure an invalid authorization code fails.
        """
        mock_exchange_code_and_get_user_profile.side_effect = ValueError("Failed to obtain access token from provider.")

        response = self.client.post(reverse('token_obtain_oauth'), {
            'provider': 'google',
            'code': 'invalid_code'
        })

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Failed to obtain access token from provider."})

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    def test_refresh_user_tokens(self, mock_exchange_code_and_get_user_profile):
        """
        Ensure an existing active user can receive new tokens.
        """
        user = User.objects.create(email='activeuser@example.com', is_active=True)
        mock_exchange_code_and_get_user_profile.return_value = ('mock_access_token', {'email': 'activeuser@example.com'})

        response = self.client.post(reverse('token_obtain_oauth'), {
            'provider': 'google',
            'code': 'mock_code'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
