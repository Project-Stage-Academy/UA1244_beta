from decimal import Decimal
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from elasticsearch_dsl import connections

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from .models import Startup, Industry, Location, FundingStage
from users.models import User, Role


User = get_user_model()

class StartupTestBase:
    """
    Initializes test data, including a user, industry, and location.
    """
    def create_common_test_data(self):
        self.startup_role = Role.objects.create(name='startup')

        user = User.objects.create_user(
            email='defaultuser@example.com',
            password='password123',
            username='defaultuser',
            first_name='Default',
            last_name='User',
        )
        user.is_active = True
        user.change_active_role('startup')
        user.save()

        industry = Industry.objects.create(name='Tech')
        location = Location.objects.create(
            city='San Francisco',
            country='USA',
            city_code='SF'
        )

        return user, industry, location

class StartupProfileAPITest(APITestCase, StartupTestBase):

    """
    Unit tests for startup profile management functionality in the API.
    This test class checks the creation, unauthorized access, invalid data handling,
    and updating of startup profiles, using Django Rest Framework's APITestCase 
    to simulate API requests.

    Methods:
        setUp(): Initializes test data and API credentials.
        test_create_profile(): Tests the creation of a valid startup profile via an authenticated 
        POST request.
        test_create_profile_unauthorized(): Tests that creating a profile without authentication 
        returns a 401 status code.
        test_create_invalid_profile(): Tests the creation of a startup profile with invalid data, 
        ensuring a 400 status code.
        test_update_profile(): Tests updating an existing startup profile with valid data and verifies
        that the data is updated.
    """

    def setUp(self):

        self.user, self.industry1, self.location = self.create_common_test_data()
        self.startup_list_url = reverse('startup-list')

        self.client.force_authenticate(user=self.user)

    def test_create_profile(self):
        data = {
            "user": self.user.pk,
            "company_name": "Test Company2",
            "description": "Test description",
            "website": "http://example.com",
            "required_funding": 100000.00,              
            "funding_stage": FundingStage.SEED,                       
            "number_of_employees": 10,                     
            "location": self.location.location_id,                
            "industries": [self.industry1.industry_id],  
            "company_logo": None,                          
            "total_funding": 50000.00,                  
            "created_at": timezone.now(),                  
            "projects": None      
        }

        response = self.client.post(self.startup_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_profile_unauthorized(self):
        self.client.force_authenticate(user=None)
        data = {
            "user": self.user.pk,
            "company_name": "Test Company3",
            "description": "Test description",
            "website": "http://example.com",
            "required_funding": 100000.00,              
            "funding_stage": FundingStage.SEED,                       
            "number_of_employees": 10,                     
            "location": self.location.location_id,                
            "industries": [self.industry1.industry_id],  
            "company_logo": None,                          
            "total_funding": 50000.00,                  
            "created_at": timezone.now(),                  
            "projects": None      
        }

        response = self.client.post(self.startup_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_invalid_profile(self):
        data = {
            "user": self.user.pk,
            "company_name": None,
            "description": "Test description",
            "website": "http://example.com",
            "required_funding": 100000.00,              
            "funding_stage": FundingStage.SEED,                       
            "number_of_employees": -10,                     
            "location": self.location.location_id,                
            "industries": [self.industry1.industry_id],  
            "company_logo": None,                          
            "total_funding": 50000.00,                  
            "created_at": timezone.now(),                  
            "projects": None      
        }
        response = self.client.post(self.startup_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("company_name", response.data)
        self.assertEqual(response.data["company_name"], ["This field may not be null."])

        self.assertIn("number_of_employees", response.data)
        self.assertEqual(response.data["number_of_employees"], ["Ensure this value is greater than or equal to 0."])

    def test_update_profile(self):
        data = {
            "user": self.user.pk,
            "company_name": "Test Company4",
            "description": "Test description",
            "website": "http://example.com",
            "required_funding": 100000.00,
            "funding_stage": FundingStage.SEED,
            "number_of_employees": 10,
            "location": str(self.location.location_id),
            "industries": [self.industry1.industry_id],
            "company_logo": None,
            "total_funding": 50000.00,
            "created_at": timezone.now(),
            "projects": None
        }

        response = self.client.post(self.startup_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn('startup_id', response.data, "Response does not contain 'startup_id'.")
        startup_id = response.data['startup_id'] 
        update_url = reverse('startup-detail', kwargs={'pk': startup_id}) 


        updated_data = {
            "user": self.user.pk,
            "company_name": "Updated Company4",
            "description": "Updated description",
            "website": "http://example.com",
            "required_funding": 150000.00,
            "funding_stage": FundingStage.SEED,
            "number_of_employees": 15,
            "location": str(self.location.location_id),
            "industries": [self.industry1.industry_id],
            "company_logo": None,
            "total_funding": 70000.00,  
            "created_at": timezone.now(),  
            "projects": None
        }

        update_response = self.client.put(update_url, updated_data, format='json')

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        updated_startup = Startup.objects.get(pk=startup_id)
        self.assertEqual(updated_startup.company_name, "Updated Company4")
        self.assertEqual(updated_startup.required_funding, Decimal("150000.00"))
        self.assertEqual(updated_startup.number_of_employees, 15)
        self.assertEqual(updated_startup.total_funding, Decimal("70000.00"))

class StartupProfileTest(TestCase, StartupTestBase):

    """
    Unit tests for startup profile creation functionality.
    This test class checks the creation of startup profiles and the associations with industries,
    using Django's TestCase to simulate database operations.
    
    Methods:
        setUp(): Initializes test data.
        test_profile_creation(): Tests startup profile creation with valid data, including
        assigning industries and verifying the correct user and company name.
    """
    def setUp(self):
        self.user, self.industry1, self.location = self.create_common_test_data()
        self.startup_list_url = reverse('startup-list')

    def test_profile_creation(self):
        profile = Startup.objects.create(
            user=self.user,
            company_name="Test Company1",   
            description="Test description", 
            website="http://example.com",
            required_funding=100000.00,
            funding_stage=FundingStage.SEED,
            number_of_employees=10,
            location=self.location,             
            company_logo=None,              
            total_funding=50000.00,
            created_at=timezone.now(),                  
        )

        profile.industries.set([self.industry1])

        self.assertEqual(profile.company_name, "Test Company1")
        self.assertEqual(self.user.username, "defaultuser")
        self.assertIn(self.industry1, profile.industries.all())


class StartupViewSetTests(APITestCase, StartupTestBase):
    """
    Unit tests for the StartupViewSet functionality.
    This test class verifies the retrieval and listing of startup profiles using 
    Django's APITestCase to simulate authenticated requests and data retrieval.

    Methods:
        setUp(): Initializes test data, including a user with 'investor' role, 
        startup profiles.
    
        test_retrieve_startup_success(): Tests retrieving an existing startup profile
        by sending a GET request to the detail view endpoint and checking the response 
        status and data accuracy.
    
        test_retrieve_startup_not_found(): Tests retrieving a non-existent startup profile 
        by sending a GET request with a random UUID, expecting a 404 response.

        test_list_startups_success(): Tests listing all available startup profiles by 
        sending a GET request to the list view endpoint and validating the response data.

        test_search_startup_no_results(): Tests searching for a non-existent startup profile 
        by sending a GET request with a search query for a non-existent company name 
        ('NonExistentCompany') and checking that the response returns 0 results.

        test_search_startup_by_company_name(): Tests searching startup profiles by a 
        partial company name by sending a GET request with a search query parameter.

        test_search_startup_case_insensitive(): Tests the case-insensitivity of the search 
        functionality by sending a GET request with a search query that differs in case 
        (e.g., 'ecoSOLUTIONS') and ensuring it matches the startup name.
    
        test_filter_startup_by_exact_company_name(): Tests filtering startup profiles 
        by an exact company name by sending a GET request with a company_name query 
        parameter.
    
        test_filter_startup_by_industry_name(): Tests filtering startup profiles based on 
        industry by sending a GET request with an industry_name query parameter.

        test_access_denied_for_non_investor(): Tests that non-investor users receive 
        a 403 Forbidden response when trying to access the startup list endpoint. 
"""
    def setUp(self):

        self.user, self.industry1, self.location = self.create_common_test_data()
        self.industry2 = Industry.objects.create(name='finance')
        investor_role = Role.objects.create(name='investor')

        self.user.change_active_role('investor')
        self.client.force_authenticate(user=self.user)

        self.startup = Startup.objects.create(
            user_id=self.user.user_id,
            company_name="EcoSolutionss",
            required_funding=7150000.00,
            funding_stage=FundingStage.SEED,
            number_of_employees=30,
            location=self.location,
            description="Eco-friendly solutions provider",
            total_funding=20000.00,
            website="https://www.ecosolutions.com",
        ) 
        self.startup2 = Startup.objects.create(
            user_id=self.user.user_id,
            company_name="Solar",
            required_funding=1000000,
            location=self.location,
        )
        self.assertTrue(Startup.objects.filter(company_name="EcoSolutionss").exists())
        self.assertTrue(Startup.objects.filter(company_name="Solar").exists())
        self.startup.industries.set([self.industry1])
        self.startup2.industries.set([self.industry2])

        self.list_url = reverse('startup-list')
        self.retrieve_url = reverse('startup-detail', args=[self.startup.startup_id])

    def test_retrieve_startup_success(self):

        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], self.startup.company_name)

    def test_retrieve_startup_not_found(self):

        non_existent_id = uuid.uuid4()
        url = reverse('startup-detail', args=[non_existent_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['detail'], "No Startup matches the given query.")

    def test_list_startups_success(self):

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue((response.data['count']) > 0)
        self.assertEqual(response.data['results'][0]['company_name'], self.startup.company_name)
    
    def test_search_startup_no_results(self):

        response = self.client.get(self.list_url, {'search': 'NonExistentCompany'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((response.data['count']), 0)

    def test_search_startup_by_company_name(self):

        response = self.client.get(self.list_url, {'search': 'Eco'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((response.data['count']), 1)
        self.assertEqual(response.data['results'][0]['company_name'], "EcoSolutionss")
    
    def test_search_startup_case_insensitive(self):

        response = self.client.get(self.list_url, {'search': 'ecoSOLUTIONS'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((response.data['count']), 1)
        self.assertEqual(response.data['results'][0]['company_name'], "EcoSolutionss")

    def test_filter_startup_by_exact_company_name(self):

        response = self.client.get(self.list_url, {'company_name': 'Solar'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((response.data['count']), 1)
        self.assertEqual(response.data['results'][0]['company_name'], "Solar")

    def test_filter_startup_by_industry_name(self):

        response = self.client.get(self.list_url, {'industry_name': self.industry2.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['count'] >= 1)
        self.assertIn(response.data['results'][0]['company_name'], ["EcoSolutionss", "Solar"])
    
    def test_access_denied_for_non_investor(self):
        self.user.change_active_role('startup')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



class StartupSearchTestCase(TestCase):
    """
    Test case for testing search, filtering, and ordering on Startup API.
    """

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username="testuser", email="testuser@example.com", password="testpass")

        self.location = Location.objects.create(city="San Francisco", country="USA", city_code="SF")

        self.industry1 = Industry.objects.create(name="Technology")
        self.industry2 = Industry.objects.create(name="Healthcare")

        self.startup1 = Startup.objects.create(
            user=self.user,
            company_name="TechCorp",
            required_funding=500000,
            funding_stage="Seed",
            number_of_employees=50,
            description="A tech startup",
            total_funding=300000,
            location=self.location
        )
        self.startup1.industries.add(self.industry1)

        self.startup2 = Startup.objects.create(
            user=self.user,
            company_name="HealthPlus",
            required_funding=1000000,
            funding_stage="Series A",
            number_of_employees=100,
            description="Healthcare innovations",
            total_funding=500000,
            location=self.location
        )
        self.startup2.industries.add(self.industry2)

        connections.create_connection(hosts=['http://localhost:9200'])

    def test_search_startup_by_company_name(self):
        """
        Test searching startups by company name.
        """
        response = self.client.get('/startups/startups/search/', {'search': 'TechCorp'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(startup['company_name'] == 'TechCorp' for startup in response.data))

    def test_filter_startup_by_funding_stage(self):
        """
        Test filtering startups by funding stage.
        """
        response = self.client.get('/startups/startups/search/', {'funding_stage': 'Seed'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(startup['funding_stage'] == 'Seed' for startup in response.data))

    def test_filter_startup_by_required_funding_range(self):
        """
        Test filtering startups by required funding range.
        """
        response = self.client.get('/startups/startups/search/', {'total_funding__gte': 400000, 'total_funding__lte': 600000})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(400000 <= startup['total_funding'] <= 600000 for startup in response.data))

    def test_filter_startup_by_location_city(self):
        """
        Test filtering startups by location city.
        """
        response = self.client.get('/startups/startups/search/', {'location.city': 'San Francisco'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(startup['location']['city'] == 'San Francisco' for startup in response.data))

    def test_order_startups_by_total_funding_ascending(self):
        """
        Test ordering startups by total funding in ascending order.
        """
        response = self.client.get('/startups/startups/search/', {'ordering': 'total_funding'})
        self.assertEqual(response.status_code, 200)
        funding_values = [startup['total_funding'] for startup in response.data]
        self.assertEqual(funding_values, sorted(funding_values))

    def test_order_startups_by_total_funding_descending(self):
        """
        Test ordering startups by total funding in descending order.
        """
        response = self.client.get('/startups/startups/search/', {'ordering': '-total_funding'})
        self.assertEqual(response.status_code, 200)
        funding_values = [startup['total_funding'] for startup in response.data]
        self.assertEqual(funding_values, sorted(funding_values, reverse=True))

    def test_order_startups_by_number_of_employees_ascending(self):
        """
        Test ordering startups by number of employees in ascending order.
        """
        response = self.client.get('/startups/startups/search/', {'ordering': 'number_of_employees'})
        self.assertEqual(response.status_code, 200)
        employee_counts = [startup['number_of_employees'] for startup in response.data]
        self.assertEqual(employee_counts, sorted(employee_counts))

    def test_order_startups_by_number_of_employees_descending(self):
        """
        Test ordering startups by number of employees in descending order.
        """
        response = self.client.get('/startups/startups/search/', {'ordering': '-number_of_employees'})
        self.assertEqual(response.status_code, 200)
        employee_counts = [startup['number_of_employees'] for startup in response.data]
        self.assertEqual(employee_counts, sorted(employee_counts, reverse=True))

