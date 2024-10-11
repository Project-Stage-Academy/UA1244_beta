from rest_framework import serializers

from .models import Project
from startups.models import Startup


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.

    This serializer validates and serializes the fields of the Project model
    for creating and updating project instances.
    """
    startup = serializers.PrimaryKeyRelatedField(queryset=Startup.objects.all())

    class Meta:
        model = Project
        fields = [
                'project_id', 'startup', 'title', 'description', 'required_amount', 'status',
                'planned_start_date', 'actual_start_date', 'planned_finish_date',
                'actual_finish_date', 'created_at', 'last_update', 'media'
        ]

    def validate_title(self, value):
        """
        Validate the uniqueness of the project title.

        Checks if a project with the same title already exists in the database.
        Raises a ValidationError if a duplicate title is found.

        Args:
            value (str): The title of the project to validate.

        Returns:
            str: The validated project title if unique.

        Raises:
            serializers.ValidationError: If the project title already exists.
        """

        if Project.objects.filter(title=value).exists():
            raise serializers.ValidationError("Project with this title already exists.")
        return value
