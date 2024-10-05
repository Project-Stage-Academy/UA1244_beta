from django.db import models
import uuid


class Location(models.Model):
    """
    Model representing a location.

    Attributes:
        city (str): The name of the city.
        country (str): The country name.
        city_code (str): An optional code representing the city.
    """
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=50, db_index=True)
    country = models.CharField(max_length=50, db_index=True)
    city_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return f"{self.city}, {self.country}"



class Startup(models.Model):
    """
    Model representing a startup.

    Attributes:
        user (ForeignKey): The user associated with the startup.
        company_name (str): The name of the startup company.
        required_funding (decimal): Required funding amount.
        funding_stage (str): The current funding stage.
        number_of_employees (int): The number of employees in the startup.
        location (ForeignKey): The location associated with the startup.
        company_logo (file): Optional company logo.
        description (str): Description of the startup.
        total_funding (decimal): Total amount of funding received.
        website (str): The website of the startup.
        created_at (datetime): Date when the startup was created.
    """
    startup_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='startups', db_index=True)
    company_name = models.CharField(max_length=150, unique=True, db_index=True)
    required_funding = models.DecimalField(max_digits=15, decimal_places=2)
    funding_stage = models.CharField(max_length=50, blank=True, null=True)
    number_of_employees = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='startups', db_index=True)
    company_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    total_funding = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    website = models.URLField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Startup'
        verbose_name_plural = 'Startups'
        ordering = ['company_name']
        constraints = [
            models.UniqueConstraint(fields=['company_name'], name='unique_company_name')
        ]

    def __str__(self):
        return self.company_name
