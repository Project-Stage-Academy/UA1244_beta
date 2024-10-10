from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from startups.models import Startup
from notifications.utils import trigger_notification

class SendMessageView(APIView):
    """
    View for sending a message from an investor to a startup and creating a notification.
    """
    def post(self, request, startup_id):
        try:
            startup = Startup.objects.get(startup_id=startup_id)
            investor = request.user.investor_profile  

            trigger_notification(
                investor=investor, 
                startup=startup, 
                project=None, 
                trigger_type='message_sent'
            )

            return Response({'message': 'Message sent successfully'}, status=status.HTTP_201_CREATED)
        except Startup.DoesNotExist:
            return Response({'error': 'Startup not found'}, status=status.HTTP_404_NOT_FOUND)