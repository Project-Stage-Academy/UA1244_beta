from django.contrib import admin
from .models import Investor


@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    """
    Admin view for the Investor model.

    This class customizes the admin interface for managing Investor objects.
    It provides functionality to:

    - Display relevant fields (company_name, user, available_funds, experience_years, location, created_at) in the list view.
    - Search Investors by company_name, user's username, and description.
    - Filter Investors by location, experience_years, and the date they were created.
    - Sort Investors by their creation date, with the newest entries shown first.
    - Make the investor_id and created_at fields read-only in the admin form.

    Attributes:
        list_display (tuple): Fields to display in the list view.
        search_fields (tuple): Fields to enable search functionality.
        list_filter (tuple): Fields to filter the list of investors.
        ordering (tuple): Ordering of the list view.
        readonly_fields (tuple): Fields that are marked as read-only in the form.
    """
    list_display = ('company_name', 'user', 'available_funds', 'experience_years', 'location', 'created_at')
    search_fields = ('company_name', 'user__username', 'description')
    list_filter = ('location', 'experience_years', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('investor_id', 'created_at')

    def get_queryset(self, request):
        """
        Override the default queryset to optimize related queries
        using select_related for the user foreign key.
        """
        queryset = super().get_queryset(request)
        return queryset.select_related('user')
