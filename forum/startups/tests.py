from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Startup, Industry, Location, FundingStage
from users.models import User


User = get_user_model()

class StartUpProfileAPITest(APITestCase):

    """
    Unit tests for startup profile management functionality in the API.
    This test class checks the creation, unauthorized access, invalid data handling,
    and updating of startup profiles, using Django Rest Framework's APITestCase 
    to simulate API requests.

    Methods:
        setUp(): Initializes test data, including a user, industry, location, and API credentials.
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
        self.user = User.objects.create_user(
            email='defaultuser@example.com',
            password='password123',
            username='defaultuser',
            first_name='Default',
            last_name='User',
        )

        self.industry1 = Industry.objects.create(name='Tech')

        self.location = Location.objects.create(
            city='San Francisco',
            country='USA',
            city_code='SF'
        )

        self.user.is_active=True
        self.user.save()

        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)


    def test_create_profile(self):
        url = reverse('startup-list')
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

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_profile_unauthorized(self):
        url = reverse('startup-list')
        self.client.credentials()
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

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_invalid_profile(self):
        url = reverse('startup-list')
        data = {
            "user": self.user.pk,
            "company_name": "",
            "description": "Test description",
            "website": "http://example.com",
            "required_funding": 100000.00,              
            "funding_stage": FundingStage.SEED,                       
            "number_of_employees": -10,                     
            "location": self.location.location_id,                
            "industries": [self.industry1.industry_id],  
            "company_logo": None,                          
            "total_funding": 50000000.00,                  
            "created_at": timezone.now(),                  
            "projects": None      
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_update_profile(self):

        create_url = reverse('startup-list')
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

        response = self.client.post(create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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

class StartupProfileTest(TestCase):

    """
    Unit tests for startup profile creation functionality.
    This test class checks the creation of startup profiles and the associations with industries,
    using Django's TestCase to simulate database operations.
    
    Methods:
        setUp(): Initializes test data, including a user, industry, and location.
        test_profile_creation(): Tests startup profile creation with valid data, including
        assigning industries and verifying the correct user and company name.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            email='defaultuser@example.com',
            password='password123',
            username='defaultuser',
            first_name='Default',
            last_name='User'
        )
        self.industry1 = Industry.objects.create(name='Tech') 
        self.location = Location.objects.create(
            city='San Francisco',
            country='USA',
            city_code='SF'
        )

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
