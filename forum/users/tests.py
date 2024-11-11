"""
Tests for user and role models.
"""
from uuid import uuid4
from unittest.mock import patch
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings

from allauth.socialaccount.models import SocialAccount, SocialLogin
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from users.adapter import CustomSocialAccountAdapter
from users.models import Role, User
from users.serializers import LoginSerializer, CustomToken
from users.tasks import send_activation_email, send_welcome_email, send_reset_password_email


class RoleTests(TestCase):
    """Tests for user roles."""

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
        self.assertEqual(
            user.active_role.name,
            'unassigned',
            "The user was not assigned the 'unassigned' role by default."
        )

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
        self.assertEqual(
            user.active_role.name,
            'startup',
            "Failed to change the role to 'startup'."
        )

        user.change_active_role('investor')
        self.assertEqual(
            user.active_role.name,
            'investor',
            "Failed to change the role to 'investor'."
        )

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
        with self.assertRaises(
            ValueError,
            msg="Role 'nonexistent' does not exist."
        ):
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
        self.assertEqual(
            user.active_role.name,
            'unassigned',
            "The user was not assigned the 'unassigned' role."
        )

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
        self.assertEqual(
            user.active_role.name,
            'startup',
            "Failed to assign the 'startup' role to the user during creation."
        )

class RolePermissionTests(APITestCase):
    """Tests for role-based permissions."""

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
    """Tests for OAuth token obtainment."""

    def authenticate_with_oauth(self, provider, code):
        """Helper function to simulate OAuth token retrieval."""
        return self.client.post(reverse('token_obtain_oauth'), {'provider': provider, 'code': code})

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    def test_missing_provider_or_code(self, mock_exchange_code_and_get_user_profile):
        """Test for missing provider or authorization code."""
        response = self.client.post(reverse('token_obtain_oauth'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Provider and code are required"})

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    def test_failed_user_profile_fetch(self, mock_exchange_code_and_get_user_profile):
        """Test handling errors during user profile fetch."""
        mock_exchange_code_and_get_user_profile.side_effect = ValueError("Failed to fetch user profile from provider.")
        response = self.authenticate_with_oauth('google', 'mock_code')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Failed to fetch user profile from provider."})

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    @patch('users.api_view.OAuthTokenObtainPairView.get_or_create_user')
    def test_inactive_user(self, mock_get_or_create_user, mock_exchange_code_and_get_user_profile):
        """Ensure inactive users do not receive tokens."""
        user = User.objects.create(email='inactiveuser@example.com', is_active=False)
        mock_exchange_code_and_get_user_profile.return_value = ('mock_access_token', {'email': 'inactiveuser@example.com'})
        mock_get_or_create_user.return_value = user

        response = self.authenticate_with_oauth('google', 'mock_code')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "User account is inactive."})

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    @patch('users.api_view.OAuthTokenObtainPairView.get_or_create_user')
    def test_user_exists(self, mock_get_or_create_user, mock_exchange_code_and_get_user_profile):
        """Ensure an existing user is not created again."""
        mock_user_data = {'email': 'existinguser@example.com'}
        user = User.objects.create(email='existinguser@example.com', is_active=True)
        mock_exchange_code_and_get_user_profile.return_value = ('mock_access_token', mock_user_data)
        mock_get_or_create_user.return_value = user

        response = self.authenticate_with_oauth('google', 'mock_code')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    def test_create_new_user(self, mock_exchange_code_and_get_user_profile):
        """Ensure a new user is created on first OAuth login."""
        mock_user_data = {'email': 'newuser@example.com'}
        mock_exchange_code_and_get_user_profile.return_value = ('mock_access_token', mock_user_data)

        response = self.authenticate_with_oauth('google', 'mock_code')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    def test_incorrect_auth_code(self, mock_exchange_code_and_get_user_profile):
        """Ensure an invalid authorization code fails."""
        mock_exchange_code_and_get_user_profile.side_effect = ValueError("Failed to obtain access token from provider.")

        response = self.authenticate_with_oauth('google', 'invalid_code')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Failed to obtain access token from provider."})

    @patch('users.api_view.OAuthTokenObtainPairView.exchange_code_and_get_user_profile')
    def test_refresh_user_tokens(self, mock_exchange_code_and_get_user_profile):
        """Ensure an existing active user can receive new tokens."""
        user = User.objects.create(email='activeuser@example.com', is_active=True)
        mock_exchange_code_and_get_user_profile.return_value = ('mock_access_token', {'email': 'activeuser@example.com'})

        response = self.authenticate_with_oauth('google', 'mock_code')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

class ResetPasswordRequestViewTests(APITestCase):
    """Tests for initiating the password reset process."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='resetuser',
            email='resetuser@example.com',
            password='password123'
        )

    @patch('users.tasks.send_reset_password_email.delay')
    def test_reset_password_request_valid_user(self, mock_send_email):
        """Test initiating password reset for an existing user."""
        response = self.client.post(reverse('reset_password_request'), {'email': 'resetuser@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_email.assert_called_once_with(self.user.user_id)

    def test_reset_password_request_invalid_user(self):
        """Test initiating password reset with a non-existent email."""
        response = self.client.post(reverse('reset_password_request'), {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ResetPasswordConfirmViewTests(APITestCase):
    """Tests for confirming and setting a new password."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='confirmuser',
            email='confirmuser@example.com',
            password='password123'
        )

    def test_reset_password_with_invalid_token(self):
        """Test resetting password with a valid token and UID."""
        token = default_token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse('reset_password_confirm', args=[uidb64, token])
        new_password_data = {'password': 'newpassword123'}
        response = self.client.post(url, new_password_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password must contain at least one uppercase letter.')
        
    def test_reset_password_with_valid_token(self):
        """Test attempting to reset password with an invalid token."""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse('password_reset_confirm', args=[uidb64, 'invalid-token'])
        response = self.client.post(url, {'password': 'newpassword123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)       
class UserActivationTests(APITestCase):
    """Tests for activating user accounts."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='activationuser',
            email='activationuser@example.com',
            password='password123',
            is_active=False
        )
        cls.unassigned_role = Role.objects.create(name='unassigned')

    @patch('users.tasks.send_welcome_email.apply_async')
    def test_activate_account(self, mock_send_email):
        """Test account activation process."""
        token = CustomToken.for_user(self.user)
        activation_url = reverse('activate', kwargs={'token': str(token)})

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        mock_send_email.assert_called_once_with(args=[self.user.user_id])

class UserSerializerTests(APITestCase):
    """Tests for UserSerializer and LoginSerializer functionality."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for UserSerializerTests.

        This method creates a role and a user instance that can be used across
        multiple tests, including data for creating a new user and verifying login.
        """
        cls.role = Role.objects.create(name="investor")
        cls.user_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'phone': '1234567890',
            'password': 'Password123!',
            'roles': [cls.role.name]
        }
        cls.existing_user = User.objects.create_user(
            email="testuser@example.com", password="password123", username="testuser"
        )

    def test_login_serializer_with_valid_credentials(self):
        """Test successful login using LoginSerializer.

        This method tests that LoginSerializer successfully authenticates
        a user with valid credentials and retrieves the correct user instance.
        """
        data = {"email": self.existing_user.email, "password": "password123"}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.existing_user)


class CustomTokenTests(APITestCase):
    """Tests for custom token functionality and its expiration time."""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for CustomTokenTests.

        This method creates a user instance that will be used to test
        the custom token's functionality and verify its expiration time.
        """
        cls.user = User.objects.create_user(email="test@example.com", password="password", username="testuser")

    def test_custom_token_lifetime(self):
        """Test the expiration time of the custom token.

        This test checks that the custom token generated for a user has
        the correct token type ('access') and a lifetime of zero days.
        """
        token = AccessToken.for_user(self.user)
        self.assertEqual(str(token.token_type), "access")
        self.assertEqual(token.lifetime.days, 0)


class CustomSocialAccountAdapterTests(TestCase):
    """Tests for CustomSocialAccountAdapter, specifically for handling social login."""

    def setUp(self):
        """Set up the test environment for CustomSocialAccountAdapterTests.

        This method initializes a request factory and creates a role that
        will be associated with the user during social account tests.
        """
        self.factory = RequestFactory()
        self.role = Role.objects.create(name="investor")
    
    @patch('users.tasks.send_welcome_email.apply_async')
    def test_save_user_social_account_activation(self, mock_send_welcome_email):
        """
        Test that a user authenticated via a social account is saved as active
        and receives a welcome email.
        """
        user = User(username='socialuser', email='socialuser@example.com', is_active=False)
        user.set_password('password123')
        social_account = SocialAccount(provider='google', uid='123456')
        sociallogin = SocialLogin(user=user, account=social_account)
        request = self.factory.get('/dummy-url/')
        request.session = self.client.session 
        adapter = CustomSocialAccountAdapter()
        saved_user = adapter.save_user(request=request, sociallogin=sociallogin)
        self.assertTrue(saved_user.is_active, "User should be activated upon social account creation.")
        mock_send_welcome_email.assert_called_once_with(args=[saved_user.user_id])

class UserEmailTasksTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )
        cls.activation_url = "http://example.com/activate"

    @patch("users.tasks.send_mail")
    def test_send_activation_email(self, mock_send_mail):
        """Test sending activation email."""
        send_activation_email(user_id=self.user.user_id, activation_url=self.activation_url)

        mock_send_mail.assert_called_once_with(
            subject="Activate Your Account",
            message=(
                f"Hi {self.user.first_name},\n\nPlease click the link below to activate your account:\n{self.activation_url}"
            ),
            from_email=None,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    @patch("users.tasks.send_mail")
    def test_send_welcome_email(self, mock_send_mail):
        """Test sending welcome email."""
        send_welcome_email(user_id=self.user.user_id)

        mock_send_mail.assert_called_once_with(
            subject="Welcome to Our Platform!",
            message=mock_send_mail.call_args[0][1],  
            from_email=None, 
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    @patch("users.tasks.send_mail")
    @patch("users.tasks.render_to_string", return_value="Rendered email content")
    def test_send_reset_password_email(self, mock_render_to_string, mock_send_mail):
        """Test sending reset password email."""
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        reset_link = f"http://example.com/reset_password/{uid}/{token}/"

        send_reset_password_email(user_id=self.user.user_id)

        mock_render_to_string.assert_called_once_with(
            "emails/reset_password_email.html", {"user": self.user, "reset_link": reset_link}
        )
        mock_send_mail.assert_called_once_with(
            subject="Password Reset Request",
            message="Rendered email content",
            from_email=None,  # Замінити на settings.EMAIL_HOST_USER
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    @patch("users.tasks.logger")
    @patch("users.tasks.send_mail")
    def test_send_activation_email_user_does_not_exist(self, mock_send_mail, mock_logger):
        """Test activation email error logging when user does not exist."""
        send_activation_email(user_id="non_existing_user_id", activation_url=self.activation_url)

        mock_logger.error.assert_called_once_with("User with ID %s does not exist", "non_existing_user_id")
        mock_send_mail.assert_not_called()

    @patch("users.tasks.logger")
    @patch("users.tasks.send_mail", side_effect=Exception("Email send failed"))
    def test_send_activation_email_failure(self, mock_send_mail, mock_logger):
        """Test logging failure to send activation email."""
        send_activation_email(user_id=self.user.user_id, activation_url=self.activation_url)

        mock_logger.error.assert_called_once_with("Failed to send activation email: %s", "Email send failed")

class UserEmailTasksTests(TestCase):
    """
    Test case for user email-related tasks, including sending activation,
    welcome, and password reset emails, as well as handling cases when
    users do not exist.
    """
    @classmethod
    def setUpTestData(cls):
        """
        Set up test data, including a test user and activation URL for email tasks.
        """
        cls.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )
        cls.activation_url = f"{settings.FRONTEND_URL}/activate"

    @patch("users.tasks.send_mail")
    def test_send_activation_email(self, mock_send_mail):
        """
        Test that the activation email is sent with the correct parameters.
        """
        send_activation_email(user_id=self.user.user_id, activation_url=self.activation_url)

        mock_send_mail.assert_called_once_with(
            subject="Activate Your Account",
            message=(
                f"Hi {self.user.first_name},\n\nPlease click the link below to activate your account:\n{self.activation_url}"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    @patch("users.tasks.logger")
    @patch("users.tasks.send_mail")
    def test_send_activation_email_user_does_not_exist(self, mock_send_mail, mock_logger):
        """
        Test that an error is logged and email is not sent when the specified user does not exist.
        """
        non_existing_uuid = uuid4()
        send_activation_email(user_id=non_existing_uuid, activation_url=self.activation_url)

        mock_logger.error.assert_called_once_with("User with ID %s does not exist", non_existing_uuid)
        mock_send_mail.assert_not_called()

    @patch("users.tasks.logger")
    @patch("users.tasks.send_mail")
    def test_send_welcome_email_user_does_not_exist(self, mock_send_mail, mock_logger):
        """
        Test that an error is logged and email is not sent when attempting to send a welcome email to a nonexistent user.
        """
        non_existing_uuid = uuid4()
        send_welcome_email(user_id=non_existing_uuid)

        mock_logger.error.assert_called_once_with("User with ID %s does not exist", non_existing_uuid)
        mock_send_mail.assert_not_called()

    @patch("users.tasks.logger")
    @patch("users.tasks.send_mail")
    def test_send_reset_password_email_user_does_not_exist(self, mock_send_mail, mock_logger):
        """
        Test that an error is logged and email is not sent when attempting to send a password reset email to a nonexistent user.
        """
        non_existing_uuid = uuid4()
        send_reset_password_email(user_id=non_existing_uuid)

        mock_logger.error.assert_called_once_with("User with ID %s does not exist", non_existing_uuid)
        mock_send_mail.assert_not_called()
