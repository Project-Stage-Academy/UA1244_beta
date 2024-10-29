from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from users.models import User

@shared_task
def send_activation_email(user_id, activation_url):
    """
    Task to send an account activation email to a user.

    This function is a shared Celery task that retrieves the user by their `user_id`, 
    constructs an activation email, and sends it to the user's registered email address.

    Args:
        user_id (int): The ID of the user to whom the activation email will be sent.
        activation_url (str): The URL that the user must click to activate their account.

    Returns:
        None. Prints a success message if the email is sent successfully or an error message 
        if the user does not exist.

    Raises:
        User.DoesNotExist: If the user with the given `user_id` does not exist in the database.
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
        print(f"Activation email sent to {user.email}")
    except User.DoesNotExist:
        print(f"User with ID {user_id} does not exist")