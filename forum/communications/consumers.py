import asyncio
import json
import logging
import urllib

from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

logger = logging.getLogger(__name__)


class BaseConsumer(AsyncWebsocketConsumer):
    MAX_RETRIES = 3

    async def connect(self):
        # Extract the token from the query string
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = urllib.parse.parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        # Validate the token
        try:
            validated_token = UntypedToken(token)
            user_id = validated_token['user_id']

            if user_id is None:
                raise DenyConnection("Invalid token: User not found")

        except (InvalidToken, TokenError):
            logger.error("Connection is denied: invalid token")
            raise DenyConnection("Invalid token")

        await self.join_group()

        await self.accept()

    async def disconnect(self, close_code):
        await self.leave_group()

    async def receive(self, text_data):

        for attempt in range(self.MAX_RETRIES):
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json["message"]

                await self.send_group_message(message)
                return
            except json.JSONDecodeError as e:
                logger.error(
                    f"Invalid JSON data received (attempt {attempt + 1}/{self.MAX_RETRIES}): {text_data}, error: {e}")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error processing message (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                await asyncio.sleep(1)

    async def join_group(self):
        """
        Override this method in subclasses to join the specific group.
        """
        raise NotImplementedError("Subclasses must implement join_group method.")

    async def leave_group(self):
        """
        Override this method in subclasses to leave the specific group.
        """
        raise NotImplementedError("Subclasses must implement leave_group method.")

    async def send_group_message(self, message):
        """
        Override this method in subclasses to send messages to the specific group.
        """
        raise NotImplementedError("Subclasses must implement send_group_message method.")


class CommunicationConsumer(BaseConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_id = None
        self.room_group_id = None

    async def join_group(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_id = f"chat_{self.room_id}"

        await self.channel_layer.group_add(self.room_group_id, self.channel_name)
        logger.info(f"Client connected to room {self.room_id}")

    async def leave_group(self):
        logger.info(f"Disconnected from room {self.room_group_id}")
        await self.channel_layer.group_discard(self.room_group_id, self.channel_name)

    async def send_group_message(self, message):
        await self.channel_layer.group_send(
            self.room_group_id, {"type": "chat.message", "message": message}
        )

    async def chat_message(self, event):
        message = event["message"]
        logger.info(f"Received message: {message}")
        await self.send(text_data=json.dumps({"message": message}))


class NotificationConsumer(BaseConsumer):
    async def join_group(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.users_group_name = f'{self.user_id}'

        await self.channel_layer.group_add(
            self.users_group_name,
            self.channel_name
        )
        logger.info(f"Client connected to notification group {self.users_group_name}")

    async def leave_group(self):
        logger.info(f"Disconnected from notification group {self.users_group_name}")
        await self.channel_layer.group_discard(
            self.users_group_name,
            self.channel_name
        )

    async def send_group_message(self, message):
        await self.channel_layer.group_send(
            self.users_group_name, {"type": "notification.message", "message": message}
        )

    async def notification_message(self, event):
        notification = event["notification"]
        logger.info(f"Received notification: {notification}")
        await self.send(text_data=json.dumps({"message": notification}))