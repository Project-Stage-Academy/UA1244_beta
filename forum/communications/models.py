import datetime
from django.db import models
from mongoengine import EmbeddedDocument, StringField, Document, DateTimeField, ListField, \
    EmbeddedDocumentField


class User(EmbeddedDocument):
    user_id = StringField(required=True)
    username = StringField(required=True)


class Message(EmbeddedDocument):
    sender = EmbeddedDocumentField(User)
    message = StringField(required=True)


class Room(Document):
    id = StringField(primary_key=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    messages = ListField(EmbeddedDocumentField(Message)) # [{"sender": {"user_id": 1, "username": "user1"}, "message": "Hello"}, {...}]
    participants = ListField(EmbeddedDocumentField(User)) # [{"user_id": 1, "username": "user1"}, {"user_id": 2, "username": "user_2"}]

    def add_message(self, sender, message):
        if sender in self.participants:
            self.messages.append(Message(sender=sender, message=message))
            self.save()
        else:
            raise ValueError("Sender must be a participant of the room.")