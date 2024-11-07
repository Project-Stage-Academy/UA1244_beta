"""
WebSocket consumer for handling real-time notifications for authenticated users.

This consumer allows users to receive notifications in real-time via WebSocket.
Users must be authenticated to connect to the WebSocket server.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time notifications.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes the consumer with user and group_name attributes.
        """
        super().__init__(*args, **kwargs)
        self.user = None
        self.group_name = None

    async def connect(self):
        """
        Handles the WebSocket connection request. Authenticates the user, adds the user to the notification group,
        and accepts the WebSocket connection if the user is authenticated.
        Closes the connection if the user is not authenticated.
        """
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        self.group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, _):
        """
        Handles WebSocket disconnection. Removes the user from the notification group.
        """
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        """
        Sends a notification message to the WebSocket client.

        Args:
            event (dict): The event containing the notification message.

        Sends:
            JSON-formatted notification message to the WebSocket.

        Handles:
            Any errors during the WebSocket communication, such as connection closures or other issues.
        """
        message = event.get('message', '')

        try:
            await self.send(text_data=json.dumps({'message': message}))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': 'An error occurred while sending the notification.',
                'details': str(e)
            }))
