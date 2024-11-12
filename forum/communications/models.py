import datetime
from django.utils import timezone

from mongoengine import EmbeddedDocument, StringField, Document, DateTimeField, ListField, \
    EmbeddedDocumentField, ReferenceField, BooleanField, ValidationError


class User(EmbeddedDocument):
    """
        Represents a user in the system.

        Attributes:
            user_id (str): The unique identifier for the user.
            username (str): The name of the user.
    """

    user_id = StringField(required=True)
    username = StringField(required=True)


class Message(EmbeddedDocument):
    """
       Represents a message sent by a user.

       Attributes:
           sender (User): The user who sent the message.
           message (str): The content of the message.
    """

    sender = EmbeddedDocumentField(User)
    message = StringField(required=True, min_length=1)
    room = ReferenceField('Room')


class Room(Document):
    """
       Represents a chat room where messages are exchanged.

       Attributes:
           created_at (datetime): The timestamp when the room was created.
           messages (List[Message]): A list of messages exchanged in the room.
           participants (List[User]): A list of users participating in the room.
    """

    created_at = DateTimeField(default=timezone.now)
    messages = ListField(EmbeddedDocumentField(Message)) # [{"sender": {"user_id": 1, "username": "user1"}, "message": "Hello"}, {...}]
    participants = ListField(EmbeddedDocumentField(User)) # [{"user_id": 1, "username": "user1"}, {"user_id": 2, "username": "user_2"}]

    def clean(self):
        if not self.participants:
            raise ValidationError("Participants list cannot be empty.")

class Notification(Document):
    """
       Represents a notification for a user related to a specific message.

       Attributes:
           user (User): The user who will receive the notification.
           message (Message): The message that the notification relates to.
           is_read (bool): Indicates whether the notification has been read.
           created_at (datetime): The timestamp when the notification was created.
    """

    user = EmbeddedDocumentField(User)
    message = EmbeddedDocumentField(Message)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=timezone.now)

    def mark_as_read(self):
        """
            Mark the notification as read.
        """
        self.is_read = True
        self.save()

    def __str__(self):
        """
            Returns a string representation of the Notification instance.
        """
        return f"Notification for {self.user.username}: {self.message.message[:20]}..."