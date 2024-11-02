import bleach
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from communications.models import Message


class UserSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    username = serializers.CharField()


class MessageSerializer(serializers.Serializer):
    class Meta:
        model = Message
        fields = '__all__'

    sender = UserSerializer()
    message = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)


class RoomSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField(read_only=True)
    messages = MessageSerializer(many=True)
    participants = UserSerializer(many=True)


class NotificationSerializer(serializers.Serializer):
    user = UserSerializer()
    message = MessageSerializer()
    is_read = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
