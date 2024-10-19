from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Startup
from .serializers import StartupSerializer
from .permissions import IsInvestorOrStartup


class StartupListView(generics.ListAPIView):
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    permission_classes = [IsAuthenticated, IsInvestorOrStartup]


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