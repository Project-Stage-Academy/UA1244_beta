from django.db import models
from projects.models import Project
from investors.models import Investor
from startups.models import Startup
from django.core.exceptions import ValidationError

class Notification(models.Model):
    """
    Model to store notifications for different types of actions within the platform.
    A notification can be related to a project, startup, or investor, and is triggered by certain events.
    """
    TRIGGER_CHOICES = [
        ('project_follow', 'Project follower or subscription change'),
        ('project_profile_change', 'Project profile updated'),
        ('startup_profile_update', 'Startup profile updated'),
        ('startup_follow', 'Startup follower or subscription change'),
        ('investor_follow', 'Investor follows startup'),
    ]

    INITIATOR_CHOICES = [
        ('investor', 'Investor'),
        ('project', 'Project'),
        ('startup', 'Startup'),
    ]

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, related_name='notifications', null=True)
    startup = models.ForeignKey(Startup, on_delete=models.SET_NULL, related_name='notifications', null=True)
    investor = models.ForeignKey(Investor, on_delete=models.SET_NULL, related_name='notifications', null=True)
    trigger = models.CharField(max_length=55, choices=TRIGGER_CHOICES)
    initiator = models.CharField(max_length=10, choices=INITIATOR_CHOICES)
    date_time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    redirection_url = models.URLField(blank=True, null=True)

    def clean(self):
        """
        Custom validation to ensure at least one related entity (project, startup, or investor) is provided.
        Raises a ValidationError if none of the related entities are set.
        """
        if not self.project and not self.startup and not self.investor:
            raise ValidationError('At least one of project, startup, or investor must be set.')

    def set_redirection_url(self):
        """
        Set the redirection URL based on the trigger and associated objects.
        If no associated object is available, assign a default testing URL.
        """
        redirection_mapping = {
            'project_follow': f'/projects/{self.project.id}/' if self.project else None,
            'startup_profile_update': f'/startups/{self.startup.id}/' if self.startup else None
        }
        self.redirection_url = redirection_mapping.get(self.trigger, 'http://example.com/fake-url-for-testing/')
        
        if not self.redirection_url:
            print('Warning: No associated project or startup for redirection')

    def save(self, *args, **kwargs):
        """
        Automatically set the redirection URL and validate the notification instance before saving.
        """
        self.clean()  
        if not self.redirection_url:
            self.set_redirection_url()
        super().save(*args, **kwargs)

    def __str__(self):
        """
        String representation of the Notification instance.
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
