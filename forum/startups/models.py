from django.db import models
import uuid
from users.models import User

from users.models import User


class FundingStage(models.TextChoices):
    SEED = 'Seed', 'Seed'
    SERIES_A = 'Series A', 'Series A'
    SERIES_B = 'Series B', 'Series B'
    SERIES_C = 'Series C', 'Series C'
    IPO = 'IPO', 'Initial Public Offering'


class Location(models.Model):
    """
    Model representing a location.

    Attributes:
        location_id (UUID): Unique identifier for the location.
        city (str): City name of the location.
        country (str): Country name of the location.
        city_code (str): Code representing the city.
    """
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    city_code = models.CharField(max_length=10, null=True)
    app_label = 'startups'



    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return f"{self.city}, {self.country}"

class CaseInsensitiveField(models.CharField):
    """
    A case-insensitive CharField that stores values in lowercase.
    """

    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            raise ValueError("max_length is required")
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        return value.lower() if value else value

    def get_prep_value(self, value):
        return value.lower() if value else value
    
class Industry(models.Model):
    """
    Model representing an industry.

    Attributes:
        industry_id (UUID): Unique identifier for the industry.
        name (str): Name of the industry.
    """
    industry_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CaseInsensitiveField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Industry'            
        verbose_name_plural = 'Industries'
        ordering = ['name'] 

    def __str__(self):
        return self.name 


class Startup(models.Model):
    """
    Model representing a startup.

    Attributes:
        user (ForeignKey): A ForeignKey pointing to the User model.
            If the user is deleted, this field will be set to null (SET_NULL).
            This ensures that the startup record can still exist even if the related user is deleted,
            but it will no longer have an active link to a specific user.
        company_name (str): The name of the startup.
        required_funding (decimal): The amount of funding required by the startup.
            The value must be non-negative.
        funding_stage (str): The stage of funding for the startup.
            Examples include "Seed", "Series A", etc.
        number_of_employees (int): The number of employees in the startup.
        location (ForeignKey): A ForeignKey pointing to the Location model.
            If the location is deleted, this field will be set to null (SET_NULL).
            This ensures that the startup record can still exist even if the related location is deleted,
            but it will no longer have an active link to a specific location.
        company_logo (ImageField): The logo of the startup, with a maximum file size of 5 MB.
        description (str): A description of the startup.
        total_funding (decimal): The total amount of funding received by the startup.
        website (str): The URL to the startup's website.
        industries (ManyToMany): A startup can belong to multiple industries.
        created_at (datetime): The date and time when the startup entry was created.
    """
    startup_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='startups')
    company_name = models.CharField(max_length=150, unique=True, db_index=True)
    required_funding = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    funding_stage = models.CharField(max_length=20, choices=FundingStage.choices, default=FundingStage.SEED)
    number_of_employees = models.PositiveIntegerField(null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='startups')
    company_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    total_funding = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    website = models.URLField(max_length=255, blank=True, null=True)
    industries = models.ManyToManyField(Industry, related_name='startups')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Startup'
        verbose_name_plural = 'Startups'
        

    def __str__(self):
        return self.company_name
