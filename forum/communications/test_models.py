from django.test import TestCase
import mongomock
from mongoengine import connect, ValidationError, disconnect

from .models import User, Message, Room, Notification


class RoomModelTest(TestCase):
    def test_room_creation_valid(self):
        user1 = User(user_id="1", username="user1")
        user2 = User(user_id="2", username="user2")
        room = Room(participants=[user1, user2])
        self.assertIsNotNone(room)

    def test_room_creation_invalid_without_participants(self):
        with self.assertRaises(ValidationError):
            room = Room()
            room.clean()

    def test_room_creation_default_created_at(self):
        room = Room(participants=[User(user_id="1", username="user1")])
        self.assertIsNotNone(room.created_at)