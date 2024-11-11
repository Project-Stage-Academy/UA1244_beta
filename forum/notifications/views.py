"""
Views for managing notification preferences for startups and investors.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views import View
from .models import StartupNotificationPreferences, InvestorNotificationPreferences

class NotificationPreferencesUpdateView(LoginRequiredMixin, View):
    """
    View to update notification preferences for both startups and investors.
    This view handles both GET and POST requests, allowing the user to view 
    and update their notification preferences.
    """

    def check_user_permission(self, user):
        """
        Check whether the user has permission to update preferences.
        The user must either be a startup or an investor.

        Args:
            user (User): The user whose permissions are being checked.

        Returns:
            bool: True if the user has permission, False otherwise.
        """
        return hasattr(user, 'startup') or hasattr(user, 'investor')

    def get_user_preferences(self, user):
        """
        Retrieve the notification preferences for the given user.
        Either returns startup or investor preferences based on the user's role.

        Args:
            user (User): The user whose preferences are being retrieved.

        Returns:
            preferences (object): The user's notification preferences.
        """
        if hasattr(user, 'startup'):
            startup = user.startup
            return StartupNotificationPreferences.objects.get_or_create(startup=startup)[0]
        
        if hasattr(user, 'investor'):
            investor = user.investor
            return InvestorNotificationPreferences.objects.get_or_create(investor=investor)[0]
        
        return None

    def get(self, request):
        """
        Handle the GET request to display the notification preferences page.
        
        If the user is a startup or an investor, their notification preferences 
        are retrieved and displayed. If the user is neither, access is denied.

        Returns:
            Rendered notification preferences page if the user is authorized.
            HttpResponseForbidden if the user is not authorized.
        """
        if not self.check_user_permission(request.user):
            messages.error(request, "You do not have permission to access this page.")
            return HttpResponseForbidden("Access denied: You are not authorized to update preferences.")

        preferences = self.get_user_preferences(request.user)
        context = {'preferences': preferences}
        return render(request, 'notifications/preferences.html', context)

    def post(self, request):
        """
        Handle the POST request to update the user's notification preferences.

        The method updates the notification preferences for either a startup 
        or an investor based on the user's role. If the user is neither, access is denied.

        Returns:
            Redirects to the notification preferences page with a success message
            upon successful update. Returns HttpResponseForbidden if the user 
            is not authorized to make updates.
        """
        if not self.check_user_permission(request.user):
            messages.error(request, "You do not have permission to update preferences.")
            return HttpResponseForbidden("Access denied: You are not authorized to update preferences.")

        preferences = self.get_user_preferences(request.user)
        preferences.email_project_updates = 'email_project_updates' in request.POST
        preferences.push_project_updates = 'push_project_updates' in request.POST
        preferences.email_startup_updates = 'email_startup_updates' in request.POST
        preferences.push_startup_updates = 'push_startup_updates' in request.POST

        preferences.save()

        messages.success(request, "Your notification preferences have been updated.")
        return redirect('notification-prefs-update')
