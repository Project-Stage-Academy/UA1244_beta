from celery import shared_task
from .utils import trigger_notification
from investors.models import Investor
from startups.models import Startup
from projects.models import Project
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def trigger_notification_task(investor_id, startup_id, project_id, trigger_type):
    try:
        investor = Investor.objects.get(investor_id=investor_id)
        startup = Startup.objects.get(startup_id=startup_id)
        project = Project.objects.get(project_id=project_id)

        
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
    Task to send an email notification to the user asynchronously.
    
    Args:
        user_email (str): The email address of the recipient.
        subject (str): The subject of the email.
        message (str): The body content of the email.
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
        subject,
        email_body,
        settings.EMAIL_HOST_USER,  
        [user_email],                 
        fail_silently=False,           
    )


@shared_task
def send_email_notification(user_email, subject, message):
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])