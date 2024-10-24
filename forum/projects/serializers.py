from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
                'project_id', 'startup', 'title', 'description', 'required_amount', 'status',
                'planned_start_date', 'actual_start_date', 'planned_finish_date',
                'actual_finish_date', 'created_at', 'last_update', 'industry', 'media'
        ]