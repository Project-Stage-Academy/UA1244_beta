from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from communications.models import Room, Message
from communications.serializers import RoomSerializer
from users.models import User

import logging

logger = logging.getLogger(__name__)


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
            user = User.objects.get_object_or_404(user_id=user_id)

            text = request.data.get("text")

            message = Message(sender={"user_id": str(user.user_id), "username": user.username}, message = text)

            Room.objects(id=conversation_id).update_one(push__messages=message)

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

            return Response(RoomSerializer(room).data['messages'], status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

