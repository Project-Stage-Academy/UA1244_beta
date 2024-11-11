"""
This module contains test cases for validating the functionality of the InvestorFollow model,
the InvestorNotificationsAPIView, and the SaveStartupView API endpoints in the investors app.

The tests verify:
- The ability for investors to follow startups and prevent duplicate follows.
- The retrieval of unread notifications for investors.
- The saving (following) of startups by investors, including error handling.
"""

import uuid
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from notifications.models import Notification
from .models import InvestorFollow, Startup, Investor

User = get_user_model()


class InvestorFollowModelTest(TestCase):
    """
    Test class for validating the functionality of the InvestorFollow model,
    which represents the many-to-many relationship between investors (users)
    and startups. This test suite ensures that investors can follow startups
    and that duplicate follow relationships cannot be created.
    """

    def setUp(self):
        """
        Setup method to initialize the test environment. It creates a user,
        an associated investor profile, and a startup. These objects will be
        used in subsequent tests to verify the behavior of the InvestorFollow model.
        """
        self.user = User.objects.create_user(
            username='investor1',
            email='investor1@example.com',
            password='testpass'
        )
        self.investor = Investor.objects.create(
            user=self.user,
            company_name="Investor's Company",
            available_funds=100000
        )
        self.startup = Startup.objects.create(
            user=self.user,
            company_name="Test Startup",
            required_funding=50000
        )

    def test_investor_can_follow_startup(self):
        """
        Test that an investor (represented by a user) can successfully follow
        a startup. The test ensures that the relationship between the investor
        and startup is created correctly, and the timestamp for when the startup
        was saved is automatically added.
        """
        relationship = InvestorFollow.objects.create(
            investor=self.investor,
            startup=self.startup
        )
        self.assertEqual(relationship.investor, self.investor)
        self.assertEqual(relationship.startup, self.startup)
        self.assertIsNotNone(relationship.saved_at)

    def test_unique_investor_startup_relationship(self):
        """
        Test that an investor cannot follow the same startup more than once.
        The test ensures that the uniqueness constraint on the InvestorFollow
        model prevents the creation of duplicate follow relationships between
        the same investor and startup.
        """
        InvestorFollow.objects.create(
            investor=self.investor,
            startup=self.startup
        )
        with self.assertRaises(IntegrityError):
            InvestorFollow.objects.create(
                investor=self.investor,
                startup=self.startup
            )


class InvestorNotificationsAPIViewTest(APITestCase):
    """
    Test class for the InvestorNotificationsAPIView, validating that unread notifications
    can be retrieved successfully and handling cases when there are no notifications.
    """

    def setUp(self):
        """
        Sets up the test environment by creating a user, an associated investor profile,
        and an authenticated API client for requests.
        """
        self.user = User.objects.create_user(
            username='investor_user',
            email='investor_user@example.com',
            password='password'
        )
        self.investor = Investor.objects.create(
            user=self.user,
            company_name="Investor's Company",
            available_funds=50000
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_unread_notifications(self):
        """
        Test that an investor can retrieve unread notifications. Verifies the correct
        status code and response data.
        """
        notification = Notification.objects.create(
            investor=self.investor,
            message="New investment opportunity",
            is_read=False
        )
        url = reverse('investor_notifications')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], notification.message)

    def test_no_notifications_found(self):
        """
        Test case when no unread notifications exist. Expects a 200 OK status
        with an empty list in the response.
        """
        url = reverse('investor_notifications')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class SaveStartupViewTest(APITestCase):
    """
    Test class for the SaveStartupView, verifying that an investor can save a startup,
    handle duplicate saves, and respond appropriately when startup or investor are not found.
    """

    def setUp(self):
        """
        Sets up the test environment by creating a user, an associated investor profile,
        a startup, and an authenticated API client for requests.
        """
        self.user = User.objects.create_user(
            username='investor_user',
            email='investor_user@example.com',
            password='password'
        )
        self.investor = Investor.objects.create(
            user=self.user,
            company_name="Investor's Company",
            available_funds=100000
        )
        self.startup = Startup.objects.create(
            user=self.user,
            company_name="Test Startup",
            required_funding=50000
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_save_startup_successfully(self):
        """
        Test that an investor can successfully save a startup.
        Expects a 201 Created status and a success message.
        """
        url = reverse('save_startup', kwargs={'startup_id': self.startup.startup_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'Startup saved successfully.')

    def test_save_startup_already_saved(self):
        """
        Test that an investor cannot save the same startup twice.
        Expects a 400 Bad Request status and an error message.
        """
        InvestorFollow.objects.create(investor=self.investor, startup=self.startup)
        url = reverse('save_startup', kwargs={'startup_id': self.startup.startup_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'You have already saved this startup.')

    def test_investor_not_found(self):
        """
        Test case where the investor is not found. Expects a 401 Unauthorized status
        when the user is not authenticated.
        """
        self.client.force_authenticate(user=None)
        url = reverse('save_startup', kwargs={'startup_id': self.startup.startup_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_startup_not_found(self):
        """
        Test case where the startup does not exist. Expects a 404 Not Found status
        and an appropriate error message.
        """
        url = reverse('save_startup', kwargs={'startup_id': uuid.uuid4()})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Startup not found')
