import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from users.models import User


logger = logging.getLogger(__name__)


@shared_task
def send_activation_email(user_id, activation_url):
    """
    Sends an activation email to the user with the specified user ID.

    This function retrieves the user based on the provided user_id,
    then sends an activation email containing a link to activate the account.
    If the user does not exist, it logs an error.

    Args:
        user_id (str): The UUID of the user to send the activation email to.
        activation_url (str): The URL that the user can click to activate their account.

    Logs:
        Sends an info log if the email was sent successfully,
        or an error log if the user is not found or the email fails to send.
    """
    try:
        user = User.objects.get(user_id=user_id)
        send_mail(
            subject='Activate Your Account',
            message=f'Hi {user.first_name},\n\nPlease click the link below to activate your account:\n{activation_url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,  
        )
        logger.info(f"Activation email sent to {user.email}")
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
    except Exception as e:
        logger.error(f"Failed to send activation email: {e}")




@shared_task
def send_welcome_email(user_id):
    """
    Sends a welcome email to the user with the specified user ID.

    This function retrieves the user based on the provided user_id,
    then sends a welcome email to greet them on joining the platform.
    If the user does not exist, it logs an error.

    Args:
        user_id (UUID): The UUID of the user to send the welcome email to.

    Logs:
        Sends an info log if the email was sent successfully,
        or an error log if the user is not found or the email fails to send.
    """
    try:
        user = User.objects.select_related().get(user_id=user_id)

        subject = "Welcome to Our Platform!"
        message = render_to_string('emails/welcome_email.html', {'username': user.username})
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        logger.info(f"Welcome email sent to {user.email}")
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist")
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")