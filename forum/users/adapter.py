from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from .tasks import send_welcome_email

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for handling the saving of users authenticated through social accounts.

    This adapter overrides the default `save_user` method to automatically activate
    social account users upon creation and send a welcome email asynchronously.
    """

    def save_user(self, request, sociallogin, form=None):
        """
        Saves the user authenticated through a social account, sets them as active,
        and sends a welcome email.

        This method is called after the user has been successfully authenticated by
        the social account provider. It sets `is_active` to `True`, saves the user,
        and triggers an asynchronous task to send a welcome email.

        Args:
            request: The HTTP request object.
            sociallogin: An instance containing the social account details.
            form: Optional; form data, if any, associated with the user.

        Returns:
            User: The saved user instance with an activated status.
        """
        user = super().save_user(request, sociallogin, form)
        user.is_active = True
        user.save()
        
        # Convert user_id to string to pass to Celery task
        user_id = str(user.user_id)
        send_welcome_email.apply_async(args=[user_id])
        
        return user
