from django.contrib import admin

from projects.models import Project
from .models import Startup, Industry, Location

class StartupIndustryInline(admin.TabularInline):
    model = Startup.industries.through
    extra = 1
class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

class StartupAdmin(admin.ModelAdmin):
    """
    Customizes the management of the Startup model in the Django admin interface.
    Displays key fields such as user, startup ID, company name, required funding, funding stage, 
    location, description, total funding, and creation date in the list view.
    Enables filtering by startup ID, company name, funding stage, location, and creation date 
    for efficient record management.
    Allows searching startups by company name, funding stage, and location for quick access to records.
    Incorporates inline management for industries and projects associated with each startup.
    
    Attributes:
    list_display (tuple): Specifies the fields to be displayed in the list view.
    list_filter (tuple): Defines the fields available for filtering in the admin list view.
    search_fields (tuple): Configures the fields searchable in the admin panel.
    fieldsets (tuple): Organizes fields into logical sections for better user experience in the admin form.
    inlines (list): Specifies inline models to be managed within the Startup admin form.
    """
    list_display = (
        'user', 'company_name', 'required_funding', 
        'funding_stage', 'location', 'total_funding', 'startup_id'
    )
    list_filter = (
        'company_name', 'funding_stage', 'location',
    )
    search_fields = (
        'company_name', 'funding_stage', 'location'
    )
    ordering = ('-created_at',)
    readonly_fields = ('startup_id', 'created_at')
    fieldsets = [('Main', {'fields': ['user', 'company_name', 'description', 'funding_stage']}),
                 ('Info', {'fields': ['required_funding', 'location', 'total_funding', 'created_at']})]
    inlines = [StartupIndustryInline, ProjectInline]

admin.site.register(Startup, StartupAdmin)

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

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

