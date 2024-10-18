from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from communications.models import Room, Message
from communications.serializers import RoomSerializer
from users.models import User


class ConversationApiView(APIView):

    def post(self, request: Request):
        try:
            if not request.data:
                return Response({"error": "Empty request body"}, status=status.HTTP_400_BAD_REQUEST)

            participants = request.data.get("participants")

            if not participants:
                return Response({"error": "Missing 'participants' key in request body"},
                                status=status.HTTP_400_BAD_REQUEST)

            if len(participants) == 0:
                return Response({"error": "'participants' empty in request body"},
                                status=status.HTTP_400_BAD_REQUEST)

            room_users = []

            # Get authenticated user. Room creator.
            authenticated_user = request.auth.payload.get("user_id")
            room_users.append(authenticated_user)

            # Map participants from Django users to Mongo users
            for user_id in participants:
                user = User.objects.get(user_id=user_id)
                room_users.append({"user_id": str(user.user_id), "username": user.username})

            # Create new room
            room = Room(messages=[], participants=room_users)
            room.save()

            return Response("Conversation created successfully!", status=status.HTTP_201_CREATED)

        except Exception as e:
            # Handle unexpected errors gracefully
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MessageApiView(APIView):
    """
    API endpoint to send message
    """
    def post(self, request: Request):
        try:
            if not request.data:
                return Response({"error": "Empty request body"}, status=status.HTTP_400_BAD_REQUEST)

            conversation_id = request.data.get("conversation_id")

            if not conversation_id:
                return Response({"error": "Missing 'conversation_id' key in request body"},
                                status=status.HTTP_400_BAD_REQUEST)

            user_id = request.auth.payload.get("user_id")
            user = User.objects.get(user_id=user_id)

            text = request.data.get("text")

            message = Message(sender={"user_id": str(user.user_id), "username": user.username}, message = text)

            Room.objects(id=conversation_id).update_one(push__messages=message)

            return Response("Message sent successfully!", status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected errors gracefully
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListMessagesApiView(APIView):
    """
    API endpoint to see list messages in a conversation:
    """
    def get(self, request: Request, conversation_id):
        try:
            if not conversation_id:
                return Response({"error": "Missing 'conversation_id' key in request URL"},
                                status=status.HTTP_400_BAD_REQUEST)

            room = Room.objects(id=conversation_id).first()

            return Response(RoomSerializer(room).data['messages'], status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected errors gracefully
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

