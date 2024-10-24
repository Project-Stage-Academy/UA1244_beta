from django.shortcuts import render
from rest_framework import viewsets
from .models import Startup
from .serializers import StartupSerializer
from rest_framework.permissions import IsAuthenticated 

class StartupViewSet(viewsets.ModelViewSet):
    """
    API view to handle CRUD operations for Startup instances.
    This view provides GET, POST, PUT methods 
    to list, create, update startup profiles. 
    It requires the user to be authenticated.
    
    Attributes:
        queryset (QuerySet): A queryset of all Startup instances.
        serializer_class (Serializer): The serializer used to validate 
        and serialize data.
        permission_classes (list): A list of permission classes 
        that determine access rights.
    """
    queryset = Startup.objects.all()
    serializer_class = StartupSerializer
    permission_classes = [IsAuthenticated]


