from django.contrib import admin
from .models import Startup, Location


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


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Location model.

    Features:
        - `list_display`: Specifies fields to display in the list view of the admin panel.
        - `search_fields`: Allows admin users to search for specific entries by city, country, or city code.
        - `ordering`: Sets the default ordering of entries in the list view by city name.
        - `list_filter`: Adds a filter sidebar to filter locations by country.
        
    Attributes:
        - list_display (tuple): Fields shown in the list view, providing quick reference to key information.
        - search_fields (tuple): Fields used for search functionality in the admin panel.
        - ordering (tuple): Default ordering of entries when displayed in the list view.
        - list_filter (tuple): Adds filter options in the admin sidebar for filtering by the selected field(s).
    """
    
    list_display = ('location_id', 'city', 'country', 'city_code')
    search_fields = ('city', 'country', 'city_code')
    ordering = ('city',)
    list_filter = ('country',)
