from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import InvestorStartup, Startup, Investor

User = get_user_model()

class InvestorStartupModelTest(TestCase):
    """
    Test class for validating the functionality of the InvestorStartup model, 
    which represents the many-to-many relationship between investors (users) 
    and startups. This test suite ensures that investors can follow startups 
    and that duplicate follow relationships cannot be created.
    """

    def setUp(self):
        """
        Setup method to initialize the test environment. It creates a user,
        an associated investor profile, and a startup. These objects will be 
        used in subsequent tests to verify the behavior of the InvestorStartup model.
        """

        self.user = User.objects.create_user(
            username='investor1',
            email='investor1@example.com',
            password='testpass'
        )

        self.investor_id = Investor.objects.create(
            user=self.user,
            company_name="Investor's Company",
            available_funds=100000
        )

        self.startup_id = Startup.objects.create(
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

        relationship = InvestorStartup.objects.create(
            investor_id=self.user,
            startup_id=self.startup_id
        )

        self.assertEqual(relationship.investor_id, self.user)
        self.assertEqual(relationship.startup_id, self.startup_id)
        self.assertIsNotNone(relationship.saved_at)

    def test_unique_investor_startup_relationship(self):
        """
        Test that an investor cannot follow the same startup more than once.
        The test ensures that the uniqueness constraint on the InvestorStartup 
        model prevents the creation of duplicate follow relationships between 
        the same investor and startup.
        """

        InvestorStartup.objects.create(
            investor_id=self.user,
            startup_id=self.startup_id
        )

        with self.assertRaises(Exception):
            InvestorStartup.objects.create(
                investor_id=self.user,
                startup_id=self.startup_id
            )

