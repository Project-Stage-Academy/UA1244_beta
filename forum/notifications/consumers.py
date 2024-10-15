import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time notifications.
    """

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

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection. Removes the user from the notification group.

        Args:
            close_code (int): The WebSocket close code.
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
            await self.send(text_data=json.dumps({
                'message': message
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': 'An error occurred while sending the notification. Please try again later.',
                'details': str(e)
            }))
