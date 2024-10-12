from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.http import HttpResponseForbidden

class NotificationPreferencesUpdateView(View):
    """
    View to update notification preferences for startups. Handles GET and POST requests.
    """

    def get(self, request):
        """
        Handle GET request to display notification preferences.

        Returns:
            Rendered preferences page if the user is a startup, otherwise an error or redirect.
        """
        if not hasattr(request.user, 'startup'):
            messages.error(request, "You do not have permission to access this page. Only startups can update preferences.")
            return HttpResponseForbidden("Access denied: You are not authorized to update preferences.")

        startup = request.user.startup
        context = {
            'startup': startup
        }
        return render(request, 'notifications/preferences.html', context)

    def post(self, request):
        """
        Handle POST request to update notification preferences.

        Returns:
            Redirects to the preferences page with a success message after updating preferences.
            If the user is not a startup, denies access.
        """
        if not hasattr(request.user, 'startup'):
            messages.error(request, "You do not have permission to update preferences. Only startups can do this.")
            return HttpResponseForbidden("Access denied: You are not authorized to update preferences.")

        startup = request.user.startup
        preferences = startup.notification_preferences

        preferences.email_project_updates = 'email_project_updates' in request.POST
        preferences.push_project_updates = 'push_project_updates' in request.POST
        preferences.email_startup_updates = 'email_startup_updates' in request.POST
        preferences.push_startup_updates = 'push_startup_updates' in request.POST

        preferences.save()
        messages.success(request, "Your notification preferences have been updated.")
        return redirect('notification-prefs-update')
