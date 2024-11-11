import json

import channels
import mongomock
import pytest
from asgiref.sync import async_to_sync
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from asgiref.testing import ApplicationCommunicator
from communications.consumers import CommunicationConsumer
from django.urls import path
from rest_framework_simplejwt.tokens import AccessToken
from mongoengine import connect, disconnect

from communications.models import Message
from communications.serializers import MessageSerializer


@pytest.mark.asyncio
class TestCommunicationConsumer:
    @pytest.fixture(autouse=True)
    def setup_database(self):
        # Connect to a test MongoDB instance
        connect('mocked_db', mongo_client_class=mongomock.MongoClient, alias='mocked')
        yield
        disconnect()

    def create_valid_token(self, user_id):
        token = AccessToken()
        token['user_id'] = user_id
        return str(token)

    async def test_connect_valid_token(self):
        valid_token = self.create_valid_token('test')
        room_id = '672f50f338ddb97bdf3ed1c0'

        application = URLRouter([
            path("ws/communications/<room_id>/", CommunicationConsumer.as_asgi()),
        ])

        communicator = WebsocketCommunicator(
            application,f"ws/communications/{room_id}/?token={valid_token}")

        connected, _ = await communicator.connect()
        assert connected

        await communicator.disconnect()

    async def test_communication_send(self):
        valid_token = self.create_valid_token('test')
        room_id = '672f50f338ddb97bdf3ed1c0'

        application = URLRouter([
            path("ws/communications/<room_id>/", CommunicationConsumer.as_asgi()),
        ])

        communicator = WebsocketCommunicator(
            application,f"ws/communications/{room_id}/?token={valid_token}")

        connected, _ = await communicator.connect()
        assert connected

        message = Message(sender={"user_id": "1", "username": "test"}, message="text")
        channel_layer = channels.layers.get_channel_layer()
        await channel_layer.group_send(
            f"chat_{room_id}", {"type": "chat.message", "message": MessageSerializer(message).data}
        )

        response = await communicator.receive_from()

        response_data = json.loads(response)
        assert response_data == {"message": {"sender": {"user_id": "1", "username": "test"}, "message": "text"}}

        await communicator.disconnect()