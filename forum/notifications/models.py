from django.db import models
from projects.models import Project
from investors.models import Investor
from startups.models import Startup
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta



def get_expiration_date():
    """
    Function to get the expiration date for the notification.
    Returns the current date and time plus 30 days.
    """
    return timezone.now() + timedelta(days=30)

class Notification(models.Model):
    """
    A model to store notifications for different actions within the platform.
    A notification can be related to a project, startup, or investor, and is triggered by specific events.
    """
    
    TRIGGER_CHOICES = [
        ('project_follow', 'Project follower or subscription change'),
        ('project_profile_change', 'Project profile updated'),
        ('startup_profile_update', 'Startup profile updated'),
        ('startup_follow', 'Startup follower or subscription change'),
        ('investor_follow', 'Investor follows startup'),
        ('investor_profile_change', 'Investor profile updated'),  # New trigger for investor profile update
    ]

    INITIATOR_CHOICES = [
        ('investor', 'Investor'),
        ('project', 'Project'),
        ('startup', 'Startup'),
        ('system', 'System'),  
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, related_name='notifications', null=True)
    startup = models.ForeignKey('startups.Startup', on_delete=models.SET_NULL, related_name='notifications', null=True)
    investor = models.ForeignKey('investors.Investor', on_delete=models.SET_NULL, related_name='notifications', null=True)
    trigger = models.CharField(max_length=55, choices=TRIGGER_CHOICES)
    initiator = models.CharField(max_length=10, choices=INITIATOR_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='low')
    date_time = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(default=get_expiration_date)  
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)  
    redirection_url = models.URLField(blank=True, null=True)

    def clean(self):
        """
        Validates that at least one related entity (project, startup, or investor) is set.
        Raises a ValidationError if none of the related entities are set.
        """
        if not self.project and not self.startup and not self.investor:
            raise ValidationError('At least one of project, startup, or investor must be set.')

    def set_redirection_url(self):
        """
        Sets the redirection URL based on the trigger and associated objects.
        Assigns a default testing URL if no associated object is found.
        """
        redirection_mapping = {
            'project_follow': f'/projects/{self.project.id}/' if self.project else None,
            'startup_profile_update': f'/startups/{self.startup.id}/' if self.startup else None,
            'investor_profile_change': f'/investors/{self.investor.id}/' if self.investor else None,
        }
        self.redirection_url = redirection_mapping.get(self.trigger, 'http://example.com/fake-url-for-testing/')
        
        if not self.redirection_url:
            print('Warning: No associated project, startup, or investor for redirection')

    def mark_as_read(self):
        """
        Marks the notification as read and sets the exact time when it was read.
        """
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

    def has_expired(self):
        """
        Checks if the notification has expired based on the expiration date.
        """
        return timezone.now() > self.expiration

    def save(self, *args, **kwargs):
        """
        Automatically sets the redirection URL, validates the notification instance, 
        and saves the instance to the database.
        """
        self.clean()  
        if not self.redirection_url:
            self.set_redirection_url()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the Notification instance.
        """
        return f'Notification {self.trigger} for {self.initiator}'


class StartupNotificationPreferences(models.Model):
    """
    Model to store notification preferences for startups.
    A startup can have multiple notification preferences for various projects.
    """
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='notification_preferences')
    email_project_updates = models.BooleanField(default=True)
    push_project_updates = models.BooleanField(default=True)
    email_startup_updates = models.BooleanField(default=True)
    push_startup_updates = models.BooleanField(default=True)

    def __str__(self):
        """
        String representation of the StartupNotificationPreferences instance.
        """
        return f'Notification Preferences for {self.startup}'


class InvestorNotificationPreferences(models.Model):
    """
    Model to store notification preferences for investors.
    An investor can have multiple notification preferences for different startups and projects.
    """
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='notification_preferences')
    email_project_updates = models.BooleanField(default=True)
    push_project_updates = models.BooleanField(default=True)
    email_startup_updates = models.BooleanField(default=True)
    push_startup_updates = models.BooleanField(default=True)

    def __str__(self):
        """
        String representation of the InvestorNotificationPreferences instance.
        """
        return f'Notification Preferences for {self.investor}'
