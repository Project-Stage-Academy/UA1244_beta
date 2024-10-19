from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Startup
from .serializers import StartupSerializer
from .permissions import IsInvestorOrStartup
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound
import logging

logger = logging.getLogger(__name__)


class StartupListView(generics.ListAPIView):
    serializer_class = StartupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Startup.objects.all()  # Використовуйте .all(), щоб отримати всі об'єкти

    def get(self, request, *args, **kwargs):
        try:
            startups = self.get_queryset()  # Використовуємо get_queryset() для доступу до даних
            if not startups.exists():
                raise NotFound(detail="No startups found.")
            
            serializer = self.serializer_class(startups, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            logger.error(f"Validation Error: {str(e)}")  # Logging the validation error
            return Response({'error': 'Data validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except NotFound as e:
            logger.warning(f"Not Found: {str(e)}")  # Logging when no startups are found
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        except PermissionDenied as e:
            logger.warning(f"Permission Denied: {str(e)}")  # Logging permission denied errors
            return Response({'error': 'You do not have permission to access this resource.'}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Internal Server Error: {str(e)}")  # Logging any other unexpected errors
            return Response({'error': 'Internal server error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class StartupDetailView(generics.RetrieveAPIView):
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    lookup_field = 'startup_id'  # Використовуємо поле 'startup_id' для пошуку

    def get_queryset(self):
        return Startup.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            startup_id = kwargs.get('startup_id')  # Отримуємо 'startup_id' замість 'uuid'
            logger.debug(f"Fetching startup with id: {startup_id}")
            
            if not startup_id:
                raise ValueError("Missing startup ID in the URL")
            
            startup = self.get_object()  # Отримуємо стартап за startup_id
            serializer = self.get_serializer(startup)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Startup.DoesNotExist:
            logger.error(f"Startup with id {kwargs['startup_id']} not found.")
            return Response({'error': 'Startup not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Internal server error: {str(e)}")
            return Response({'error': 'Internal server error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SendMessageView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        startup_id = request.data.get('startup_id')
        content = request.data.get('content')
        
        if not startup_id or not content:
            return Response({"error": "Startup ID and content are required."}, status=400)

        startup = Startup.objects.get(pk=startup_id)
        
        # Here you would handle saving the message (this is simplified)
        # For example:
        # Message.objects.create(startup=startup, content=content, sender=request.user)
        
        return Response({"success": f"Message sent to {startup.company_name}"})