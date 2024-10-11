from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Project


@receiver(post_save, sender=Project)
def project_updated(sender, instance, created, **kwargs):
    """
    Signal receiver for project updates.

    This function is triggered after a Project instance is saved. It sends
    an update message to the corresponding WebSocket group, notifying
    connected clients of the project's latest details.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Project): The instance of the Project that was saved.
        created (bool): A flag indicating whether a new instance was created.
        **kwargs: Additional keyword arguments passed to the receiver.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'project_{instance.project_id}',
        {
            'type': 'project_update',
            'message': {
                'id': str(instance.project_id),
                'title': instance.title,
                'description': instance.description,
            }
        }
    )
