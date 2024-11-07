from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from elasticsearch_dsl.connections import connections


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




class ProjectSearchTestCase(TestCase):
    """Test case for Project search functionality in Elasticsearch."""

    def setUp(self):
        """Set up test data for Project search tests."""
        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="testpass")
        self.startup = Startup.objects.create(
            user=self.user,
            company_name="TechCorp",
            required_funding=200000,
            funding_stage="Seed",
            number_of_employees=50,
            description="A tech startup"
        )
        self.project1 = Project.objects.create(
            startup=self.startup,
            title="AI Research",
            description="Research in AI technologies",
            required_amount=1000000,
            status="planned"
        )
        self.project2 = Project.objects.create(
            startup=self.startup,
            title="Healthcare App Development",
            description="Healthcare technology development",
            required_amount=500000,
            status="completed"
        )
        connections.create_connection(hosts=['http://localhost:9200'])

    def test_search_project_by_title(self):
        """Test searching projects by title."""
        response = self.client.get('/projects/search/', {'search': 'AI'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(project['title'] == 'AI Research' for project in response.data))

    def test_search_project_by_description(self):
        """Test searching projects by description."""
        response = self.client.get('/projects/search/', {'search': 'technology'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(project['description'] == 'Healthcare technology development' for project in response.data))

    def test_filter_project_by_status(self):
        """Test filtering projects by status."""
        response = self.client.get('/projects/search/', {'status': 'completed'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(project['status'] == 'completed' for project in response.data))

    def test_filter_project_by_required_amount_range(self):
        """Test filtering projects by required funding amount range."""
        response = self.client.get('/projects/search/', {'required_amount__gte': 300000, 'required_amount__lte': 800000})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(300000 <= project['required_amount'] <= 800000 for project in response.data))

    def test_filter_project_by_startup_name(self):
        """Test filtering projects by associated startup name."""
        response = self.client.get('/projects/search/', {'startup.company_name': 'TechCorp'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(project['startup']['company_name'] == 'TechCorp' for project in response.data))

    def test_order_projects_by_title_ascending(self):
        """Test ordering projects by title in ascending order."""
        response = self.client.get('/projects/search/', {'ordering': 'title'})
        self.assertEqual(response.status_code, 200)
        titles = [project['title'] for project in response.data]
        self.assertEqual(titles, sorted(titles))

    def test_order_projects_by_title_descending(self):
        """Test ordering projects by title in descending order."""
        response = self.client.get('/projects/search/', {'ordering': '-title'})
        self.assertEqual(response.status_code, 200)
        titles = [project['title'] for project in response.data]
        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_order_projects_by_required_amount_ascending(self):
        """Test ordering projects by required funding amount in ascending order."""
        response = self.client.get('/projects/search/', {'ordering': 'required_amount'})
        self.assertEqual(response.status_code, 200)
        amounts = [project['required_amount'] for project in response.data]
        self.assertEqual(amounts, sorted(amounts))

    def test_order_projects_by_required_amount_descending(self):
        """Test ordering projects by required funding amount in descending order."""
        response = self.client.get('/projects/search/', {'ordering': '-required_amount'})
        self.assertEqual(response.status_code, 200)
        amounts = [project['required_amount'] for project in response.data]
        self.assertEqual(amounts, sorted(amounts, reverse=True))

    