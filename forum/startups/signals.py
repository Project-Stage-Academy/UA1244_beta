from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Startup
from .document import StartupDocument
from notifications.models import Notification
from investors.models import InvestorFollow
from notifications.tasks import create_notification_task


@receiver(post_save, sender=Startup)
def notify_investors_on_startup_update(sender, instance, created, **kwargs):
    """
    Signal handler to notify investors when a startup's profile is updated or a new post is created.
    
    When a `Startup` instance is saved, this function checks if the instance is newly created or updated.
    If created, it sets a message for a new post. If updated, it generates a message for a profile update.
    
    The function then retrieves all investors following the startup and creates a notification for each one.
    For profile updates, an asynchronous task is triggered to handle additional notification actions.
    
    Parameters:
        sender (Model): The model class sending the signal, `Startup` in this case.
        instance (Startup): The instance of `Startup` that was created or updated.
        created (bool): A boolean indicating if the instance is newly created (True) or updated (False).
        **kwargs: Additional keyword arguments passed to the signal.
    
    Notification:
        Creates a notification entry for each investor following the startup.
        - If `created` is True, the notification indicates a new post.
        - If `created` is False, the notification indicates a profile update.
    
    Asynchronous Task:
        If the startup is updated (not created), this function also triggers an asynchronous task to
        manage further notification processing.
    """

    followers = InvestorFollow.objects.filter(startup=instance).select_related('investor')

    for follow in followers:
        Notification.objects.create(
            investor=follow.investor,
            startup=instance,
            trigger='startup_profile_update',
            redirection_url=f'/startups/{instance.startup_id}/'
        )

    if not created:
        create_notification_task.delay(
            'startup',
            instance.startup_id,
            'startup_profile_update',
            f"Startup '{instance.company_name}' has updated its profile.",
            initiator='startup'
        )


@receiver(post_save, sender=Startup)
def update_startup_document(sender, instance, **kwargs):
    """
    Signal to update the Elasticsearch document for the Startup model when an instance is saved.

    Args:
        sender: The model class.
        instance: The instance being saved.
        kwargs: Additional keyword arguments.
    """
    StartupDocument().update(instance)

@receiver(post_delete, sender=Startup)
def delete_startup_document(sender, instance, **kwargs):
    """
    Signal to delete the Elasticsearch document for the Startup model when an instance is deleted.

    Args:
        sender: The model class.
        instance: The instance being deleted.
        kwargs: Additional keyword arguments.
    """
    StartupDocument().delete(instance)