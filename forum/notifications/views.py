from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages

class NotificationPreferencesUpdateView(View):
    def get(self, request):
        startup = request.user.startup
        context = {
            'startup': startup
        }
        return render(request, 'notifications/preferences.html', context)

    def post(self, request):
        startup = request.user.startup
        preferences = startup.notification_preferences

        preferences.email_project_updates = 'email_project_updates' in request.POST
        preferences.push_project_updates = 'push_project_updates' in request.POST
        preferences.email_startup_updates = 'email_startup_updates' in request.POST
        preferences.push_startup_updates = 'push_startup_updates' in request.POST

        preferences.save()
        messages.success(request, "Your notification preferences have been updated.")
        return redirect('notification-prefs-update')