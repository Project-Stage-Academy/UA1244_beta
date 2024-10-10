from .models import Notification

def trigger_notification(investor, startup, project, trigger_type, initiator='investor'):
    """
    Function to create a notification for a specific action.

    Args:
        investor (Investor): The investor triggering the notification.
        startup (Startup): The startup receiving the notification.
        project (Project): The project associated with the action.
        trigger_type (str): The type of action triggering the notification.
        initiator (str): The initiator of the action (default 'investor').

    Returns:
        Notification: The created notification instance.
    """
    notification = Notification.objects.create(
        investor=investor,
        startup=startup,
        project=project,
        trigger=trigger_type,
        initiator=initiator,
        redirection_url=f'/projects/{project.id}/'
    )
    return notification