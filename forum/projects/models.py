from django.db import models
from startups.models import Startup
import uuid

class Media(models.Model):
    """
    Model representing media files related to a project.

    Attributes:
        image_url (str): URL to the image.
        video_url (str): URL to the video.
        business_plan (str): URL to the business plan document.
        project_logo (str): URL to the project logo.
    """
    media_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image_url = models.URLField(max_length=150, blank=True, null=True)
    video_url = models.URLField(max_length=150, blank=True, null=True)
    business_plan = models.URLField(max_length=150, blank=True, null=True)
    project_logo = models.URLField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name = 'Media'
        verbose_name_plural = 'Media'

    def __str__(self):
        return f"Media {self.id}"

class Project(models.Model):
    """
    Model representing a project.

    Attributes:
        startup (ForeignKey): The startup associated with the project.
        title (str): Title of the project.
        description (str): A detailed description of the project.
        required_amount (decimal): The amount of funding required.
        status (str): The status of the project.
        planned_start_date (date): Planned start date of the project.
        actual_start_date (date): Actual start date of the project.
        planned_finish_date (date): Planned finish date of the project.
        actual_finish_date (date): Actual finish date of the project.
        created_at (datetime): Date when the project was created.
        last_update (datetime): Last update date of the project.
        media (ForeignKey): Associated media information for the project.
    """
    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    startup = models.ForeignKey('Startup', on_delete=models.CASCADE, related_name='projects', db_index=True)
    title = models.CharField(max_length=100, db_index=True)
    description = models.CharField(max_length=2000)
    required_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('planned', 'Planned'),
        ('in progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='planned')
    planned_start_date = models.DateField(blank=True, null=True)
    actual_start_date = models.DateField(blank=True, null=True)
    planned_finish_date = models.DateField(blank=True, null=True)
    actual_finish_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    media = models.ForeignKey(Media, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', db_index=True)

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['startup', 'title']
        constraints = [
            models.UniqueConstraint(fields=['startup', 'title'], name='unique_project_per_startup')
        ]

    def __str__(self):
        return self.title