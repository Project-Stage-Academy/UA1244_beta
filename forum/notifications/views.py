from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.views import View
from .models import StartupNotificationPreferences, InvestorNotificationPreferences


class NotificationPreferencesUpdateView(View):
    """
    View to update notification preferences for both startups and investors.
    This view handles both GET and POST requests, allowing the user to view 
    and update their notification preferences.
    """

    def get_user_preferences(self, user):
        """
        Retrieve the notification preferences for the given user, depending 
        on whether the user is a startup or an investor.

        Args:
            user (User): The user for whom to retrieve preferences.

        Returns:
            preferences (object): The user's notification preferences.
            HttpResponseForbidden: If the user does not have permission.
        """
        if hasattr(user, 'startup'):
            startup = user.startup
            return StartupNotificationPreferences.objects.get_or_create(startup=startup)[0]

        elif hasattr(user, 'investor'):
            investor = user.investor
            return InvestorNotificationPreferences.objects.get_or_create(investor=investor)[0]

        else:
            messages.error(self.request, "You do not have permission to access this page. Only startups or investors can update preferences.")
            return HttpResponseForbidden("Access denied: You are not authorized to update preferences.")

    def get(self, request):
        """
        Handle the GET request to display the notification preferences page.
        
        If the user is a startup or an investor, their notification preferences 
        are retrieved and displayed. If the user is neither, access is denied.

        Returns:
            Rendered notification preferences page if the user is authorized.
            HttpResponseForbidden if the user is not authorized.
        """
        preferences = self.get_user_preferences(request.user)
        if isinstance(preferences, HttpResponseForbidden):
            return preferences

        context = {
            'preferences': preferences,
        }
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
        preferences = self.get_user_preferences(request.user)
        if isinstance(preferences, HttpResponseForbidden):
            return preferences

        preferences.email_project_updates = 'email_project_updates' in request.POST
        preferences.push_project_updates = 'push_project_updates' in request.POST
        preferences.email_startup_updates = 'email_startup_updates' in request.POST
        preferences.push_startup_updates = 'push_startup_updates' in request.POST

        preferences.save()

        messages.success(request, "Your notification preferences have been updated.")
        return redirect('notification-prefs-update')