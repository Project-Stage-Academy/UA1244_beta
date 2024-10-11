from django.db import models
from projects.models import Project
from investors.models import Investor
from startups.models import Startup

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

    def save(self, *args, **kwargs):
        """
        Automatically set the redirection URL based on the notification trigger type.
        If no redirection URL is provided, it assigns a default URL.
        """
        if not self.redirection_url:
            if self.trigger == 'project_follow' and self.project:
                self.redirection_url = f'/projects/{self.project.id}/'
            elif self.trigger == 'startup_profile_update' and self.startup:
                self.redirection_url = f'/startups/{self.startup.id}/'
            else:
                self.redirection_url = 'http://example.com/fake-url-for-testing/'
                print('Warning: No associated project or startup for redirection')
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
