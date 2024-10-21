from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    username = serializers.CharField()

class MessageSerializer(serializers.Serializer):
    sender = UserSerializer()
    message = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)

class RoomSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField(read_only=True)
    messages = MessageSerializer(many=True)
    participants = UserSerializer(many=True)