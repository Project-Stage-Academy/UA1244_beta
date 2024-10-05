from django.db import models
from startups.models import Startup
import uuid
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError



class Media(models.Model):
    """
    Model representing media files related to a project.

    Attributes:
        media_id (UUID): Unique identifier for the media file.
        image_url (str): URL to the image.
        video_url (str): URL to the video.
        business_plan (str): URL to the business plan document.
        project_logo (str): URL to the project logo.
    """
    media_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image_url = models.URLField(max_length=255, blank=True, null=True)
    video_url = models.URLField(max_length=255, blank=True, null=True)
    business_plan = models.URLField(max_length=255, blank=True, null=True)
    project_logo = models.URLField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Media'
        verbose_name_plural = 'Media'

    def __str__(self):
        return f"Media {self.media_id}"



class ProjectStatus(models.TextChoices):
    PLANNED = 'planned', _('Planned')
    IN_PROGRESS = 'in progress', _('In Progress')
    COMPLETED = 'completed', _('Completed')

class Project(models.Model):
    """
    Model representing a project.

    Attributes:
        project_id (UUID): Unique identifier for the project.
        startup (ForeignKey): Reference to the Startup that owns the project.
        title (str): Title of the project.
        description (TextField): Detailed description of the project.
        required_amount (Decimal): Funding amount required.
        status (str): Status of the project (planned, in progress, completed).
        planned_start_date (date): Planned start date of the project.
        actual_start_date (date): Actual start date of the project.
        planned_finish_date (date): Planned finish date of the project.
        actual_finish_date (date): Actual finish date of the project.
        created_at (datetime): Timestamp of when the project was created.
        last_update (datetime): Timestamp of the last update to the project.
        media (ForeignKey): Reference to the Media associated with the project.
    """
    project_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE, related_name='projects', db_index=True)
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    required_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.PLANNED)
    planned_start_date = models.DateField(blank=True, null=True)
    actual_start_date = models.DateField(blank=True, null=True)
    planned_finish_date = models.DateField(blank=True, null=True)
    actual_finish_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_update = models.DateTimeField(auto_now=True)
    media = models.ForeignKey('Media', on_delete=models.SET_NULL, null=True, related_name='projects')

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def clean(self):
        if self.actual_finish_date and self.planned_start_date:
            if self.actual_finish_date < self.planned_start_date:
                raise ValidationError(_('Actual finish date cannot be earlier than planned start date.'))

    def __str__(self):
        return self.title