from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from elasticsearch_dsl import connections

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from .models import Startup, Industry, Location, FundingStage
from users.models import User


User = get_user_model()

class StartupTestBase:
    """
    Initializes test data, including a user, industry, and location.
    """
    def create_common_test_data(self):
        user = User.objects.create_user(
            email='defaultuser@example.com',
            password='password123',
            username='defaultuser',
            first_name='Default',
            last_name='User',
        )
        user.is_active = True
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