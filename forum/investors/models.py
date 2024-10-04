from django.db import models
from startups.models import Location



class Investor(models.Model):
    """
    Model representing an investor.

    Attributes:
        user (ForeignKey): The user associated with the investor.
        company_name (str): The name of the investor's company.
        available_funds (decimal): Available funds for investment.
        experience_years (int): The years of experience of the investor.
        location (ForeignKey): The location associated with the investor.
        company_logo (file): Optional company logo.
        description (str): Description of the investor's company.
        website (str): The website of the company.
        created_at (datetime): Date when the investor was created.
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='investors', db_index=True)
    company_name = models.CharField(max_length=150, unique=True, db_index=True)
    available_funds = models.DecimalField(max_digits=15, decimal_places=2)
    experience_years = models.IntegerField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='investors', db_index=True)
    company_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    website = models.URLField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        verbose_name = 'Investor'
        verbose_name_plural = 'Investors'
        ordering = ['company_name']
        constraints = [
            models.UniqueConstraint(fields=['company_name'], name='unique_investor_company_name')
        ]

    
    def __str__(self):
        return self.company_name