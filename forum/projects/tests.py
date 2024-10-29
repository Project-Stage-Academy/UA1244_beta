from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from uuid import uuid4

from startups.models import Startup
from .models import ProjectStatus
from projects.models import Project

User = get_user_model()


class ProjectTests(APITestCase):
    """
    Unit tests for project management functionality in the API.

    This test class checks the creation of projects and retrieval of project history,
    using Django Rest Framework's APITestCase to simulate API requests.

    Methods:
        setUp(): Initializes test data, including a user, a startup, and API credentials.
        test_get_project_history(): Tests that a non-existent project's history returns a 404 status code.
        test_create_project(): Tests project creation by making an authenticated POST request to the API.
    """

    def setUp(self):
        """
        Sets up the test environment with a user, startup, and API authentication.
        This method creates a user and startup object, generates an access token for the user,
        and sets the necessary credentials for API authentication. It also initializes
        the URLs for project history and project management endpoints.
        """

        self.user = User.objects.create_user(
                username='testuser',
                password='testpass',
                email='testuser@example.com'
        )

        self.startup = Startup.objects.create(
            company_name="Test Startup1",
            user=self.user,
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        self.project_id = uuid4()
        self.history_url = reverse(
                'project-history', kwargs={'project_id': self.project_id}
        )
        self.management_url = reverse('project-management')

    def test_get_project_history(self):
        """
        Tests that retrieving a project's history returns a 404 error if the project does not exist.

        This method sends a GET request to the project history endpoint using a non-existent project ID.
        """

        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_history_failure(self):
        """Test retrieving history for a non-existent project returns 404"""

        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_history_success(self):
        """Test retrieving history for an existing project"""

        project_history_url = reverse('project-history', kwargs={'project_id': self.project.project_id})

        response = self.client.get(project_history_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('history', response.data)
        self.assertEqual(response.data['project_id'], str(self.project.project_id))

    def test_create_project(self):
        """
        Tests the creation of a new project via an authenticated POST request.

        This method sends a POST request with project data to the project management API and
        verifies that the response status is 201 (Created).
        """

        self.client.force_authenticate(user=self.user)

        startup = Startup.objects.create(
            company_name="Test Startup",
            user=self.user
        )

        data = {
            'startup': startup.pk,
            'title': 'New Project Title',
            'description': 'A test project description',
            'required_amount': '10000.00',
            'status': ProjectStatus.PLANNED,
            'planned_start_date': '2024-10-10',
            'planned_finish_date': '2024-12-10',
            'media': None
        }

        response = self.client.post(self.management_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        project = Project.objects.get(title='New Project Title')

        self.assertEqual(project.startup, startup)
        self.assertEqual(project.title, data['title'])
        self.assertEqual(project.description, data['description'])
        self.assertEqual(str(project.required_amount), data['required_amount'])
        self.assertEqual(project.status, data['status'])
        self.assertEqual(str(project.planned_start_date), data['planned_start_date'])
        self.assertEqual(str(project.planned_finish_date), data['planned_finish_date'])
        self.assertIsNone(project.media)


class UserAcceptanceTests(APITestCase):
    """
    Unit tests for user acceptance scenarios in project management.

    This test class focuses on the ability of authenticated users to create projects via the API.

    Methods:
        setUp(): Initializes test data, including a user, a startup, and API credentials.
        test_user_can_create_project(): Tests that an authenticated user can successfully create a project.
    """

    def setUp(self):
        """
        Sets up the test environment with a user, startup, and API authentication.

        This method creates a user and startup object, generates an access token for the user,
        and sets the necessary credentials for API authentication. It also initializes
        the URL for the project management endpoint.
        """

        self.user = User.objects.create_user(
                username='testuser2',
                password='testpass2',
                email='testuser2@example.com'
        )

        self.startup = Startup.objects.create(
            company_name="Test User Startup",
            user=self.user,
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(
                HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        self.management_url = reverse('project-management')

    def test_user_can_create_project(self):
        """
        Tests that an authenticated user can create a new project.

        This method sends a POST request with project data to the project management API and
        verifies that the response status is 201 (Created).
        """
        data = {
            'startup': self.startup.pk,
            'title': 'User Project',
            'description': 'A description for the user project',
            'required_amount': '5000.00',
            'status': ProjectStatus.PLANNED,
            'planned_start_date': '2024-10-10',
            'planned_finish_date': '2024-12-10'
        }

        response = self.client.post(self.management_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        project = Project.objects.get(title='User Project')

        self.assertEqual(project.startup, self.startup)
        self.assertEqual(project.title, data['title'])
        self.assertEqual(project.description, data['description'])
        self.assertEqual(str(project.required_amount), data['required_amount'])
        self.assertEqual(project.status, data['status'])
        self.assertEqual(str(project.planned_start_date), data['planned_start_date'])
        self.assertEqual(str(project.planned_finish_date), data['planned_finish_date'])

    def test_missing_required_fields(self):
        data = {
            'startup': self.startup.pk,
            'description': 'A description for the user project',
            'required_amount': '5000.00',
            'status': ProjectStatus.PLANNED,
            'planned_start_date': '2024-10-10',
            'planned_finish_date': '2024-12-10'
        }

        response = self.client.post(self.management_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_data_types(self):
        data = {
            'startup': self.startup.pk,
            'title': 'User Project',
            'description': 'A description for the user project',
            'required_amount': 'invalid_amount',  # Should be numeric
            'status': ProjectStatus.PLANNED,
            'planned_start_date': '2024-10-10',
            'planned_finish_date': '2024-12-10'
        }

        response = self.client.post(self.management_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_user_cannot_create_project(self):
        self.client.credentials()

        data = {
            'startup': self.startup.pk,
            'title': 'Unauthorized Project',
            'description': 'A description for unauthorized project',
            'required_amount': '3000.00',
            'status': ProjectStatus.PLANNED,
            'planned_start_date': '2024-10-10',
            'planned_finish_date': '2024-12-10'
        }

        response = self.client.post(self.management_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
