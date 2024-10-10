from django.db import models
from projects.models import Project
from investors.models import Investor
from startups.models import Startup

class Notification(models.Model):
    """
    Model to store notifications for different types of actions within the platform.
    """
    TRIGGER_CHOICES = [
        ('project_follow', 'Project follower or subscription change'),
        ('project_profile_change', 'Project profile updated'),
        ('startup_profile_update', 'Startup profile updated'),
        ('startup_follow', 'Startup follower or subscription change'),
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
        if not self.redirection_url:
            if self.trigger == 'project_follow':
                self.redirection_url = f'/projects/{self.project.id}/'
            elif self.trigger == 'startup_profile_update':
                self.redirection_url = f'/startups/{self.startup.id}/'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Notification {self.trigger} for {self.initiator}'

class StartupNotificationPreferences(models.Model):
    """
    Model to store notification preferences for startups.
    """
    startup = models.OneToOneField(Startup, on_delete=models.CASCADE, related_name='notification_preferences')
    email_project_updates = models.BooleanField(default=True)
    push_project_updates = models.BooleanField(default=True)
    email_startup_updates = models.BooleanField(default=True)
    push_startup_updates = models.BooleanField(default=True)

    def __str__(self):
        return f'Notification Preferences for {self.startup}'

class InvestorNotificationPreferences(models.Model):
    """
    Model to store notification preferences for investors.
    """
    investor = models.OneToOneField(Investor, on_delete=models.CASCADE, related_name='notification_preferences')
    email_project_updates = models.BooleanField(default=True)
    push_project_updates = models.BooleanField(default=True)
    email_startup_updates = models.BooleanField(default=True)
    push_startup_updates = models.BooleanField(default=True)

    def __str__(self):
        return f'Notification Preferences for {self.investor}'