from rest_framework import serializers
from .models import Startup

class StartupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Startup
        fields = ['startup_id', 'company_name', 'description', 'website', 'required_funding']