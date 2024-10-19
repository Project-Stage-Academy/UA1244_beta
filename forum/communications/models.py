import datetime

from mongoengine import EmbeddedDocument, StringField, Document, DateTimeField, ListField, \
    EmbeddedDocumentField


class User(EmbeddedDocument):
    user_id = StringField(required=True)
    username = StringField(required=True)


class Message(EmbeddedDocument):
    sender = EmbeddedDocumentField(User)
    message = StringField(required=True, min_length=1)

class Room(Document):
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    messages = ListField(EmbeddedDocumentField(Message)) # [{"sender": {"user_id": 1, "username": "user1"}, "message": "Hello"}, {...}]
    participants = ListField(EmbeddedDocumentField(User)) # [{"user_id": 1, "username": "user1"}, {"user_id": 2, "username": "user_2"}]
