from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth import get_user_model
from startups.models import Startup
from startups.models import Location
import uuid
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from users.models import User

from users.models import User


def validate_image_size(value):
    """
    Validates the size of the uploaded image.
    Args:
        value (File): The uploaded image file to validate.
    Raises:
        ValidationError: If the file size exceeds the limit.
    """
    max_size_kb = 5120  
    if value.size > max_size_kb * 1024:
        raise ValidationError(f"The maximum file size allowed is {max_size_kb}KB")


class Investor(models.Model):
    """
    Model representing an investor.

    Attributes:
        investor_id (UUID): Unique identifier for the investor.
        user (ForeignKey): Reference to the User who owns the investor profile. If the User is deleted, the investor profile is also deleted (on_delete=models.CASCADE).
        company_name (str): Name of the investor's company.
        available_funds (Decimal): Amount of funds available for investment. This field ensures that the available funds cannot be negative by using a validator.
        experience_years (int): Number of years of investment experience. This is a positive integer since negative experience years are not allowed.
        location (ForeignKey): Reference to the Location of the investor's company. When the associated location is deleted, the location is set to null (on_delete=models.SET_NULL), allowing the investor to continue to exist even if the location is no longer available.
        company_logo (ImageField): Image representing the investor's company logo. Includes validation to limit the file size to a maximum of 5 MB.
        description (TextField): Detailed description of the investor's company. Allows more characters compared to CharField.
        website (str): Website URL of the investor's company. URLField is used to ensure proper URL format.
        created_at (datetime): Timestamp of when the investor was created. This is automatically set to the current time when the object is created.
    """
    investor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investors')
    company_name = models.CharField(max_length=150, db_index=True)
    available_funds = models.DecimalField(max_digits=15, decimal_places=2, null=True, validators=[MinValueValidator(0)])
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='investors')
    company_logo = models.ImageField(upload_to='logos/', blank=True, null=True, validators=[validate_image_size])
    description = models.TextField(blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Investor'
        verbose_name_plural = 'Investors'

    def __str__(self):
        return self.company_name


class InvestorFollow(models.Model):
    """
    Represents a many-to-many relationship between investors and startups, 
    indicating which investors are following which startups.

    Attributes:
        investor_id (ForeignKey): A reference to the User model, representing 
        the investor who follows a startup. The relationship is set to cascade 
        on deletion, meaning if the user is deleted, their follows will also be removed.

        startup_id (ForeignKey): A reference to the Startup model, representing 
        the startup being followed by the investor. Like the investor, this relationship 
        also cascades on deletion.

        saved_at (DateTimeField): A timestamp indicating when the investor 
        started following the startup. This field is automatically set to 
        the current date and time when the relationship is created.
    """
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='startup_investors')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['investor', 'startup'], name='unique_investor_startup')
        ]

    def __str__(self):
        return f"{self.investor.username} follows {self.startup.company_name}"
