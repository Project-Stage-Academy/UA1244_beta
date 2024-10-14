from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db import IntegrityError
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

