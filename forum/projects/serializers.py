from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.

    This serializer validates and serializes the fields of the Project model
    for creating and updating project instances.
    """
    class Meta:
        model = Project
        fields = [
                'project_id', 'startup', 'title', 'description', 'required_amount', 'status',
                'planned_start_date', 'actual_start_date', 'planned_finish_date',
                'actual_finish_date', 'created_at', 'last_update', 'media'
        ]

    def validate_name(self, value):
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

        if Project.objects.filter(name=value).exists():
            raise serializers.ValidationError("Project with this name already exists.")
        return value
