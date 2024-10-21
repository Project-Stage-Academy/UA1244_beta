from django.contrib import admin
from .models import Startup

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    """
    Admin view for the Startup model.

    This class customizes the admin interface for managing Startup objects.
    It provides the following functionalities:

    - Displays key fields (company_name, user, required_funding, funding_stage, location, created_at) in the list view.
    - Enables search functionality on company_name, user's username, and description.
    - Filters the startups by funding stage, location, and number of employees.
    - Orders the startups by creation date, showing the newest ones first.
    - Makes the startup_id and created_at fields read-only in the admin form.
    
    Attributes:
        list_display (tuple): Fields to display in the list view.
        search_fields (tuple): Fields used for the search functionality.
        list_filter (tuple): Fields to filter startups.
        ordering (tuple): Orders the startups in the admin view.
        readonly_fields (tuple): Fields marked as read-only in the form.
    """
    list_display = ('company_name', 'user', 'required_funding', 'funding_stage', 'location', 'created_at')
    search_fields = ('company_name', 'user__username', 'description')
    list_filter = ('funding_stage', 'location', 'number_of_employees', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('startup_id', 'created_at')
