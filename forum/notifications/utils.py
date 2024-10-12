from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification
from django.core.exceptions import ValidationError




def trigger_notification(investor, startup, project, trigger_type, initiator='investor'):
    """
    Function to create a notification and send a real-time notification via WebSocket.
    """
    if not (investor or startup or project):
        raise ValidationError('Notification must be related to either an investor, startup, or project.')

    notification = Notification.objects.create(
        investor=investor,
        startup=startup,
        project=project,
        trigger=trigger_type,
        initiator=initiator,
        redirection_url=f'/projects/{project.project_id}/' if project else ''
    )

    if startup and startup.user:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{startup.user.id}',
            {
                'type': 'send_notification',
                'message': f"New notification: {trigger_type}",
            }
        )

def notify_user(user, event_type, message):
    """
    Function to check user's email notification preferences and send an email if applicable.
    
    Args:
        user (User): The user who will receive the notification.
        event_type (str): The type of event triggering the notification (e.g., 'new_follow', 'new_message').
        message (str): The content of the email to send.
    
    Returns:
        str: Message indicating the status of the notification sending.
    """
    send_email = False

    if hasattr(user, 'investor'):
        prefs = user.investor.notification_preferences
        event_map = {
            'new_follow': prefs.email_project_updates,
            'project_update': prefs.email_project_updates
        }
    elif hasattr(user, 'startup'):
        prefs = user.startup.notification_preferences
        event_map = {
            'project_update': prefs.email_project_updates,
            'startup_update': prefs.email_startup_updates
        }
    else:
        return "User does not have the required role of investor or startup."

    send_email = event_map.get(event_type, False)

    if send_email:
        from .tasks import send_email_notification
        send_email_notification.delay(user.email, f'New {event_type} notification', message)
        return f"Notification sent to {user.email}."
    
    return "Notification preferences do not allow sending an email."