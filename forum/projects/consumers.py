import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from channels.exceptions import DenyConnection


class ProjectConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling project updates.

    This consumer allows clients to connect to a specific project group,
    send messages, and receive updates related to that project.
    """

    async def connect(self):
        """
        Handle the WebSocket connection.
        This method retrieves the project ID from the URL, adds the
        channel to the project group, and accepts the connection only if the user is authenticated.
        """

        if not self.scope['user'].is_authenticated:
            await self.close(code=4001)
            return

        project_id = self.scope['url_route']['kwargs']['project_id']
        if not self.user_has_access_to_project(self.scope['user'], project_id):
            await self.close(code=4003)
            return

        self.project_id = project_id
        self.project_group_name = f'project_{self.project_id}'

        await self.channel_layer.group_add(
            self.project_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        Handle the WebSocket disconnection.

        This method removes the channel from the project group when
        the client disconnects.

        Args:
            close_code (int): The code indicating the reason for closure.
        """

        await self.channel_layer.group_discard(
            self.project_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON data.'
            }))
            return

        message = text_data_json.get('message')

        if not message:
            await self.send(text_data=json.dumps({
                'error': 'No message key in the received data.'
            }))
            return

        await self.channel_layer.group_send(
            self.project_group_name,
            {
                'type': 'project_update',
                'message': message
            }
        )

    async def project_update(self, event):
        """
        Send a project update to the WebSocket.

        This method is called when a project update is received from the
        channel layer. It sends the message back to the WebSocket client.

        Args:
            event (dict): The event data containing the message.
        """

        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
