from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

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