from django.contrib import admin
from projects.models import Project
from .models import Startup

class IndustryInline(admin.TabularInline):
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
        'user', 'startup_id', 'company_name', 'required_funding', 
        'funding_stage', 'location', 'description', 
        'total_funding', 'created_at'
    )
    list_filter = (
        'startup_id', 'company_name',
        'funding_stage', 'location', 'created_at'
    )
    search_fields = (
        'company_name', 'funding_stage', 'location'
    )
    readonly_fields = ('created_at',)  
    fieldsets = [('Main', {'fields': ['user', 'company_name', 'description', 'funding_stage']}),
                 ('Info', {'fields': ['required_funding', 'location', 'total_funding', 'created_at']})]
    inlines = [IndustryInline, ProjectInline]

admin.site.register(Startup, StartupAdmin)
