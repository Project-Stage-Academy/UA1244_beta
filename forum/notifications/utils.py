"""
Utility functions for handling notifications in the Notifications app.

These functions include methods to trigger notifications for investors, startups, or projects
and to notify users via WebSocket or email based on their preferences.
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ValidationError
from .models import Notification
from .tasks import send_email_notification


def trigger_notification(investor, startup, project, trigger_type, initiator='investor'):
    """
    Function to create a notification and send a real-time notification via WebSocket.
    
    Args:
        investor (Investor): Investor related to the notification.
        startup (Startup): Startup related to the notification.
        project (Project): Project related to the notification.
        trigger_type (str): Type of event triggering the notification.
        initiator (str): Entity initiating the notification (default is 'investor').
    
    Raises:
        ValidationError: If no related entity is provided for the notification.
    """
    if not (investor or startup or project):
        raise ValidationError(
            'Notification must be related to either an investor, startup, or project.'
        )

    Notification.objects.create(
        investor=investor,
        startup=startup,
        project=project,
        trigger=trigger_type,
        initiator=initiator,
        redirection_url=f'/projects/{project.project_id}/' if project else ''
    )

    if startup and startup.user:
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications_{startup.user.id}',
                {
                    'type': 'send_notification',
                    'message': f"New notification: {trigger_type}",
                }
            )
        except Exception as e:
            print(f"Error sending WebSocket notification: {str(e)}")


def notify_user(user, event_type, message):
    """
    Function to check user's email notification preferences and send an email if applicable.
    
    Args:
        user (User): The user who will receive the notification.
        event_type (str): The type of event triggering the notification.
        message (str): The content of the email to send.
    
    Returns:
        str: Message indicating the status of the notification sending.
    """
    if hasattr(user, 'investor'):
        prefs = getattr(user.investor, 'notification_preferences', None)
        event_map = {
            'new_follow': prefs.email_project_updates if prefs else False,
            'project_update': prefs.email_project_updates if prefs else False
        }
    elif hasattr(user, 'startup'):
        prefs = getattr(user.startup, 'notification_preferences', None)
        event_map = {
            'project_update': prefs.email_project_updates if prefs else False,
            'startup_update': prefs.email_startup_updates if prefs else False
        }
    else:
        return "User does not have the required role of investor or startup."

    send_email = event_map.get(event_type, False)

    if send_email:
        try:
            send_email_notification.delay(user.email, f'New {event_type} notification', message)
            return f"Notification sent to {user.email}."
        except Exception as e:
            return f"Failed to send email: {str(e)}"
    
    return "Notification preferences do not allow sending an email."
