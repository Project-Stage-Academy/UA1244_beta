from django.db import models
from startups.models import Startup
from investors.models import Investor
import uuid
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal
from simple_history.models import HistoricalRecords


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
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def funding_received(self):
        """
          Calculate the total funding received for the project.

          If funding is based on monetary contributions, it sums the funded_amount.
          If funding is based on percentage shares, it calculates the total share and ensures it does not exceed 100%.
        """
        funded_amount_by_now = (self.subscribed_projects.aggregate(models.Sum('funded_amount'))['funded_amount__sum']
                                or Decimal('0.00'))

        # can be also used if needed.
        # funded_share_by_now = self.subscribed_projects.aggregate(models.Sum('investment_share'))['investment_share__sum']
        # or Decimal('0.00')

        return funded_amount_by_now


def clean(self):
    if self.actual_finish_date and self.planned_start_date:
        if self.actual_finish_date < self.planned_start_date:
            raise ValidationError(_('Actual finish date cannot be earlier than planned start date.'))


def __str__(self):
    return self.title


class Subscription(models.Model):
    """
        Model represents a subscription to a project by an investor.

        This model captures the details of an investment made by an investor in a specific project.

        Attributes:
            funding_id (UUIDField): The unique identifier for the subscription. Automatically generated.
            project_id (ForeignKey): A reference to the associated project. When the project is deleted, this
                field will be set to null.
            investor_id (ForeignKey): A reference to the investor making the subscription. When the investor
                is deleted, this field will be set to null.
            funded_amount (DecimalField): The amount of money that has been funded by the investor for the project.
            funded_at (DateTimeField): The timestamp when the funding was made. Automatically set when the
                subscription is created.
            investment_share (DecimalField): The percentage share of the investment in relation to the total
                required amount of the project. Limited to a maximum of 5 digits with 2 decimal places.
            is_rejected (BooleanField): Indicates whether the subscription has been rejected. Defaults to False.
            rejection_reason (CharField): The reason for the rejection if the subscription is rejected.

        """
    FUNDING_TYPE_CHOICES = [
        ('equity', 'Equity Funding'),
        ('loan', 'Loan Funding'),
        ('grant', 'Grant'),
    ]
    funding_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True,
                                   related_name='subscribed_projects')
    investor_id = models.ForeignKey(Investor, on_delete=models.SET_NULL, null=True, related_name='projects',
                                    db_index=True)
    funded_amount = models.DecimalField(max_digits=15, decimal_places=2)
    funded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    funding_type = models.CharField(max_length=20, choices=FUNDING_TYPE_CHOICES, default='equity')
    investment_share = models.DecimalField(max_digits=5, decimal_places=2)
    is_rejected = models.BooleanField(default=False)
    rejection_reason = models.CharField(max_length=255, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project_id', 'investor_id'], name='unique_project_investor')
        ]

    def clean(self):
        super().clean()
        if self.funded_amount < 0:
            raise ValidationError(_('Funded amount must be a positive number.'))

        if self.project_id:
            total_share = self.project_id.subscribed_projects.aggregate(models.Sum('investment_share'))[
                              'investment_share__sum'] or 0
        else:
            total_share = 0

        if total_share + self.investment_share > 100:
            raise ValidationError(_('Total investment share for this project cannot exceed 100%.'))

        # validate correctness of the "validation_reason" field
        if not self.is_rejected and self.rejection_reason:
            raise ValidationError(_('The field should be empty'))
        if self.is_rejected and not self.rejection_reason:
            raise ValidationError(_('The reason of rejection should be provided.'))

    def save(self, *args, **kwargs):
        self.clean()
        if not self.funded_amount:
            raise ValidationError(_("Funded amount must be provided."))

        if not self.project_id or not self.project_id.required_amount:
            raise ValidationError(_("Project must have a valid ID and required amount."))

        self.investment_share = (self.funded_amount / self.project_id.required_amount) * 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Subscription {self.funding_id} by Investor {self.investor_id} for {self.investment_share}% ' \
               f'of the project'
