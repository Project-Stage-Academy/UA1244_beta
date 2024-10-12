from celery import shared_task
from .utils import trigger_notification
from investors.models import Investor
from startups.models import Startup
from projects.models import Project
from django.conf import settings
import aiosmtplib
from email.message import EmailMessage

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

        trigger_notification(investor, startup, project, trigger_type)

    except Investor.DoesNotExist:
        print(f'Investor with ID {investor_id} does not exist')
        return 'Investor not found'
    except Startup.DoesNotExist:
        print(f'Startup with ID {startup_id} does not exist')
        return 'Startup not found'
    except Project.DoesNotExist:
        print(f'Project with ID {project_id} does not exist')
        return 'Project not found'
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        return 'Unexpected error occurred'



@shared_task
async def send_email_notification(user_email, subject, message):
    """
    Asynchronous Celery task to send an email notification to a user using aiosmtplib.

    Args:
        user_email (str): The recipient's email address.
        subject (str): The subject of the email notification.
        message (str): The body content of the email message.
    """
    email_body = f"""
    Hello,

    You have a new notification:

    {message}

    Please log in to your account to view more details.

    Best regards,
    The Platform Team
    """

    email_message = EmailMessage()
    email_message["From"] = settings.EMAIL_HOST_USER
    email_message["To"] = user_email
    email_message["Subject"] = subject
    email_message.set_content(email_body)

    try:
        await aiosmtplib.send(
            email_message,
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
        )
    except aiosmtplib.SMTPException as e:
        print(f"Error occurred while sending email: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")