from rest_framework import serializers
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from .models import Project, Subscription
from startups.models import Startup
from .models import Subscription


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

    def validate(self, data):
        """
        Ensure that planned_finish_date is after planned_start_date.
        """
        planned_start_date = data.get('planned_start_date')
        planned_finish_date = data.get('planned_finish_date')

        if planned_start_date and planned_finish_date:
            if planned_finish_date < planned_start_date:
                raise serializers.ValidationError("Planned finish date cannot be earlier than the planned start date.")

        return data

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
        startup = self.initial_data.get('startup')

        if Project.objects.filter(title=value, startup=startup).exists():
            raise serializers.ValidationError("A project with this title already exists for this startup.")

        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

    def validate(self, data):
        project = data.get('project_id')
        funded_amount = data.get('funded_amount')
        investment_share = data.get('investment_share', 0)

        if not project:
            raise serializers.ValidationError(_("A valid project must be provided."))

        total_investment_share = project.subscribed_projects.aggregate(
            models.Sum('investment_share')
        )['investment_share__sum'] or 0

        if total_investment_share >= 100:
            raise serializers.ValidationError(_("Project is fully funded. No further subscriptions are allowed."))

        if total_investment_share + investment_share > 100:
            raise serializers.ValidationError(_(f"The total investment share cannot exceed 100%."
                                                f"Current total is {total_investment_share}%."))
        if funded_amount <= 0:
            raise serializers.ValidationError(_("Funded amount must be a positive number."))

        return data

    def create(self, validated_data):

        project = validated_data.get('project_id')
        funded_amount = validated_data.get('funded_amount')
        validated_data['investment_share'] = (funded_amount / project.required_amount) * 100
        subscription = Subscription.objects.create(**validated_data)
        
        return subscription
