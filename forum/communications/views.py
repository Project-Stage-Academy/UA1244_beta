import logging
import os
from datetime import datetime

import channels.layers

from asgiref.sync import async_to_sync
from cryptography.fernet import Fernet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from communications.models import Room, Message, Notification
from communications.serializers import MessageSerializer, NotificationSerializer
from communications.serializers import RoomSerializer
from users.models import User


logger = logging.getLogger(__name__)

cipher = Fernet(os.environ.get('FERNET_KEY'))

class ConversationApiView(APIView):

    def post(self, request: Request):
        try:
            if not request.data:
                err_msg = "Empty request body"
                logger.error(f"Error occurred: {err_msg}")
                return Response({"error": "Empty request body"}, status=status.HTTP_400_BAD_REQUEST)

            participants = request.data.get("participants")

            if not participants:
                err_msg = "Missing 'participants' key in request body"
                logger.error(f"Error occurred: {err_msg}")
                return Response({"error": "Missing 'participants' key in request body"},
                                status=status.HTTP_400_BAD_REQUEST)

            if len(participants) == 0:
                err_msg = "'participants' empty in request body"
                logger.error(f"Error occurred: {err_msg}")
                return Response({"error": "'participants' empty in request body"},
                                status=status.HTTP_400_BAD_REQUEST)

            room_users = []

            # Get authenticated user. Room creator.
            authenticated_user = request.user
            room_users.append({"user_id": str(authenticated_user.user_id), "username": authenticated_user.username})

            # Map participants from Django users to Mongo users
            for user_id in participants:
                user = User.objects.get(user_id=user_id)
                room_users.append({"user_id": str(user.user_id), "username": user.username})

            # Create new room
            room = Room(messages=[], participants=room_users)
            room.save()

            logger.info(f"Conversation {str(room.id)} created successfully!")
            return Response(f"Conversation {str(room.id)} created successfully!", status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MessageApiView(APIView):
    """
    API endpoint to send message
    """
    def post(self, request: Request):
        try:
            if not request.data:
                err_msg = "Empty request body"
                logger.error(f"Error occurred: {err_msg}")
                return Response({"error": err_msg}, status=status.HTTP_400_BAD_REQUEST)

            conversation_id = request.data.get("conversation_id")

            if not conversation_id:
                err_msg = "Missing 'conversation_id' key in request body"
                logger.error(f"Error occurred: {err_msg}")
                return Response({"error": err_msg},
                                status=status.HTTP_400_BAD_REQUEST)

            user_id = request.user.user_id

            user = get_object_or_404(User, user_id=user_id)

            text = request.data.get("text")
            encrypted_text = cipher.encrypt(text.encode()).decode()

            message = Message(sender={"user_id": str(user.user_id), "username": user.username}, message = encrypted_text)

            Room.objects(id=conversation_id).update_one(push__messages=message)

            # Send websocket message
            message.message = text
            channel_layer = channels.layers.get_channel_layer()
            try:
                async_to_sync(channel_layer.group_send)(
                    f"chat_{str(conversation_id)}", {"type": "chat.message", "message": MessageSerializer(message).data}
                )
                logger.info(f'Message sent to: chat_{str(conversation_id)}')

            except Exception as e:
                logger.error(f'Failed to send message to: chat_{str(conversation_id)}: {str(e)}')


            room = Room.objects(id=conversation_id).first()

            receivers = [receiver for receiver in room.participants if receiver.user_id != str(user_id)]

            # Display the filtered users
            for receiver in receivers:
                notification = Notification(
                    user=receiver,
                    message=message,
                    is_read=False,
                    created_at=datetime.now()
                )

                try:
                    async_to_sync(channel_layer.group_send)(f"{str(receiver.user_id)}", {
                        "type": "notification.message",
                        "notification": NotificationSerializer(notification).data})
                    logger.info(f'Notification sent to room: chat_{room.id}')

                except Exception as e:
                    logger.error(f'Failed to send notification to room {room.id}: {str(e)}')

            return Response("Message sent successfully!", status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListMessagesApiView(APIView):
    """
    API endpoint to see list messages in a conversation:
    """
    def get(self, request: Request, conversation_id):
        try:
            if not conversation_id:
                err_msg = "Missing 'conversation_id' key in request URL"
                logger.error(f"Error occurred: {err_msg}")
                return Response({"error": err_msg},
                                status=status.HTTP_400_BAD_REQUEST)

            room = Room.objects(id=conversation_id).first()

            encrypted_messages = RoomSerializer(room).data['messages']

            messages = []
            for encrypted_message in encrypted_messages:
                messages.append(cipher.decrypt(encrypted_message['message'].encode()).decode())

            return Response(messages, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

