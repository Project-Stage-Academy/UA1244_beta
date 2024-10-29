import json
import logging
import urllib

from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

logger = logging.getLogger(__name__)


class CommunicationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_id = None
        self.room_group_id = None

    async def connect(self):
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = urllib.parse.parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        try:
            validated_token = UntypedToken(token)
            user_id = validated_token['user_id']

            if user_id is None:
                raise DenyConnection("Invalid token: User not found")

        except (InvalidToken, TokenError):
            logger.error("Connection is denied: invalid token")
            raise DenyConnection("Invalid token")

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_id = f"chat_{self.room_id}"

        # Join room group
        try:
            await self.channel_layer.group_add(self.room_group_id, self.channel_name)
            logger.info(f"Client connected to room {self.room_id}")

            await self.accept()

        except Exception as e:
            logger.error(f"Error connecting to room {self.room_id}: {e}")


    async def disconnect(self, close_code):
        # Leave room group
        logger.info(f"Disconnected from room  {self.room_group_id}")
        await self.channel_layer.group_discard(self.room_group_id, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_id, {"type": "chat.message", "message": message}
            )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data received: {text_data}, error: {e}")
            print(f"Error decoding JSON: {e}")

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        logger.info(f"Received message: {message}")

        await self.send(text_data=json.dumps({"message": message}))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.users_group_name = f'{self.user_id}'

        try:
            # Join the user notification group
            await self.channel_layer.group_add(
                self.users_group_name,
                self.channel_name
            )
            logger.info(f"Client connected to notification group {self.users_group_name}")
            await self.accept()

        except Exception as e:
            logger.error(f"Error connecting to notification group {self.users_group_name}: {e}")

    async def disconnect(self, close_code):
        logger.info(f"Disconnected from notification group  {self.users_group_name}")
        await self.channel_layer.group_discard(
            self.users_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            notification = text_data_json["message"]

            # Send message to room group
            await self.channel_layer.group_send(
                self.users_group_name, {"type": "notification.message", "message": notification}
            )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON data received: {text_data}, error: {e}")
            print(f"Error decoding JSON: {e}")

    # Receive notification from notification group
    async def notification_message(self, event):
        notification = event["notification"]
        logger.info(f"Received notification: {notification}")

        await self.send(text_data=json.dumps({"message": notification}))