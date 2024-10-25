from allauth.account.signals import email_confirmed
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver
from .tasks import send_welcome_email

@receiver(email_confirmed)
def send_welcome_email_after_confirmation(request, email_address, **kwargs):
    user = email_address.user
    if SocialAccount.objects.filter(user=user).exists():
        send_welcome_email.delay(user.email, user.first_name)
