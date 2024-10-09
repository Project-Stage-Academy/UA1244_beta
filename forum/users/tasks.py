from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from users.models import User

@shared_task
def send_activation_email(user_id, activation_url):
    try:
        user = User.objects.get(user_id=user_id)
        send_mail(
            subject='Activate Your Account',
            message=f'Hi {user.first_name},\n\nPlease click the link below to activate your account:\n{activation_url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,  
        )
    except User.DoesNotExist:
        pass