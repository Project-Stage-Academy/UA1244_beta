from celery import shared_task
from .utils import trigger_notification
from investors.models import Investor
from startups.models import Startup
from projects.models import Project
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def trigger_notification_task(investor_id, startup_id, project_id, trigger_type):
    """
    Celery task to trigger a notification asynchronously for a given investor, startup, and project.

    Args:
        investor_id (int): ID of the investor triggering the notification.
        startup_id (int): ID of the startup involved in the notification.
        project_id (int): ID of the project related to the notification.
        trigger_type (str): Type of the trigger that caused the notification, such as 'project_follow' or 'startup_profile_update'.
    
    This task will handle cases where the investor, startup, or project may not exist,
    and print an error message if any of the objects are not found.
    """
    try:
        investor = Investor.objects.get(investor_id=investor_id)
        startup = Startup.objects.get(startup_id=startup_id)
        project = Project.objects.get(project_id=project_id)

        # Call the utility function to handle the notification logic
        trigger_notification(investor, startup, project, trigger_type)

    except Investor.DoesNotExist:
        print(f'Investor with ID {investor_id} does not exist')
    except Startup.DoesNotExist:
        print(f'Startup with ID {startup_id} does not exist')
    except Project.DoesNotExist:
        print(f'Project with ID {project_id} does not exist')


@shared_task
def send_email_notification(user_email, subject, message):
    """
    Celery task to send an email notification asynchronously to a user.

    Args:
        user_email (str): The recipient's email address.
        subject (str): The subject of the email notification.
        message (str): The body content of the email message.

    This task constructs a complete email body including a greeting and a notification message,
    and sends the email using the Django email backend.
    """
    email_body = f"""
    Hello,

    You have a new notification:

    {message}

    Please log in to your account to view more details.

    Best regards,
    The Platform Team
    """
    
    send_mail(
        subject,                      # Email subject
        email_body,                   # Full message body including greeting and details
        settings.EMAIL_HOST_USER,     # Sender's email, defined in Django settings
        [user_email],                 # Recipient's email
        fail_silently=False,          # Raise an error if sending fails
    )