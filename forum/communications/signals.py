import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

from .models import Message, Notification

logger = logging.getLogger('forum')

@receiver(post_save, sender=Message)
def send_notification_via_channels(sender, instance, created, **kwargs):
    """
    Create a notification and broadcast it through Channels when a new message is sent.

    Args:
        sender (Model): The model class that sent the signal (Message).
        instance (Message): The actual instance of the message that was created.
        created (bool): A boolean indicating whether the instance was created.
    """
    if created:
        room = instance.room
        if room:
            for participant in room.participants:
                if participant.user_id != instance.sender.user_id:

                    try:
                        Notification.objects.create(
                            user=participant,
                            message=instance,
                            is_read=False,
                            created_at=timezone.now()
                        )

                        notification_data = {
                            'user': participant.username,
                            'message': instance.message,
                            'is_read': False,
                        }

                        channel_layer = get_channel_layer()

                        async_to_sync(channel_layer.group_send)(
                            f'chat_{room.id}',
                            {
                                'type': 'send_notification',
                                'notification': notification_data,
                            }
                        )   
                        logger.info(f'Notification sent to group chat_{room.id} for user {participant.username}')

                    except Exception as e:
                        logger.error(f'Error creating notification or sending to channels: {str(e)}')
