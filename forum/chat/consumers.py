import json
from channels.generic.websocket import WebsocketConsumer
import logging

logger = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        logger.info("WebSocket connection established")
        self.accept()

        self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "Now you are connected!"
        }))
