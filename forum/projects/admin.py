from django.contrib import admin
from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    """
    Customizes the display and management of the Project model in the Django admin interface.

    This class configures the appearance and behavior of the Project model in the Django admin panel.

    Key Features:
    - Displays key fields such as title, startup, required amount, and status in the list view.
    - Enables filtering by status, startup, and various date fields for easier record management.
    - Allows searching projects by title, description, and the associated startup's company name.
    - Provides read-only fields for creation and last update timestamps.
    - Organizes form fields into fieldsets, including sections for project details, dates, and timestamps.

    Attributes:
    list_display (tuple): Specifies the fields to be displayed in the list view.
    list_filter (tuple): Defines the fields available for filtering in the admin list view.
    search_fields (tuple): Configures the fields searchable in the admin panel.
    readonly_fields (tuple): Marks certain fields as read-only to prevent modification.
    fieldsets (tuple): Organizes fields into logical sections for better user experience in the admin form.
    """

    list_display = (
        'title', 'startup', 'required_amount', 'status',
        'planned_start_date', 'planned_finish_date', 'created_at'
    )

    list_filter = (
        'status', 'startup', 'planned_start_date',
        'planned_finish_date', 'created_at'
    )

    search_fields = (
        'title', 'description',
        'startup__company_name'
    )

    readonly_fields = ('created_at', 'last_update')

    fieldsets = (
        (None, {
            'fields': (
                'startup', 'title', 'description',
                'required_amount', 'status', 'media'
            )
        }),
        ('Dates', {
            'fields': (
                'planned_start_date', 'actual_start_date',
                'planned_finish_date', 'actual_finish_date'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'last_update'
            )
        }),
    )


admin.site.register(Project, ProjectAdmin)
