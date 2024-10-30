from rest_framework import serializers
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models, transaction
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from .models import Project, Subscription
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
        funded_amount = Decimal(data.get('funded_amount')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        investment_share = Decimal(data.get('investment_share', 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if not project:
            raise serializers.ValidationError(_("A valid project must be provided."))

        user = self.context.get('request').user
        if not user.is_authenticated:
            raise serializers.ValidationError(_("You must be logged in to create a subscription."))
        if getattr(user, 'active_role', None) != 'Investor':
            raise serializers.ValidationError(
                _("Only users with an active role of 'Investor' can subscribe to projects."))

        total_investment_share = Decimal(project.subscribed_projects.aggregate(
            models.Sum('investment_share')
        )['investment_share__sum'] or 0).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if total_investment_share >= Decimal('100.00'):
            raise serializers.ValidationError(_("Project is fully funded. No further subscriptions are allowed."))

        if total_investment_share + investment_share > Decimal('100.00'):
            raise serializers.ValidationError(_(f"The total investment share cannot exceed 100%."
                                                f"Current total is {total_investment_share}%."))
        if funded_amount <= Decimal('0.00'):
            raise serializers.ValidationError(_("Funded amount must be a positive number."))
        data['funded_amount'] = funded_amount

        return data

    def create(self, validated_data):
        with transaction.atomic():
            project = validated_data.get('project_id')
            #locking the project row to avoid concurrency
            project = Project.objects.select_for_update().get(pk=project.pk)
            required_amount = Decimal(project.required_amount)
            if required_amount <= Decimal('0.01'):
                raise serializers.ValidationError(
                    _("Project required amount must be greater than zero to calculate investment share."))

            funded_amount = Decimal(validated_data.get('funded_amount')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            validated_data['investment_share'] = ((funded_amount / required_amount) * Decimal('100.00')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
            subscription = Subscription.objects.create(**validated_data)

        return subscription
