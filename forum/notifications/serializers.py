from rest_framework import serializers
from .models import Notification, StartupNotificationPreferences, InvestorNotificationPreferences

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    This serializer handles the serialization and deserialization of Notification
    objects and includes fields like id, trigger, is_read, redirection_url, and date_time.
    """
    class Meta:
        model = Notification
        fields = ['id', 'trigger', 'is_read', 'redirection_url', 'date_time']

class StartupNotificationPrefsSerializer(serializers.ModelSerializer):
    """
    Serializer for the StartupNotificationPreferences model.
    This serializer handles the serialization and deserialization of notification preferences
    specific to startups, including fields for email and push notifications for project and startup updates.
    """
    class Meta:
        model = StartupNotificationPreferences
        fields = ['email_project_updates', 'push_project_updates', 'email_startup_updates', 'push_startup_updates']

class InvestorNotificationPrefsSerializer(serializers.ModelSerializer):
    """
    Serializer for the InvestorNotificationPreferences model.
    This serializer handles the serialization and deserialization of notification preferences
    specific to investors, including fields for email and push notifications for project and startup updates.
    """
    class Meta:
        model = InvestorNotificationPreferences
        fields = ['email_project_updates', 'push_project_updates', 'email_startup_updates', 'push_startup_updates']

class TriggerNotificationSerializer(serializers.Serializer):
    """
    Serializer for triggering notifications based on user actions.
    This serializer includes required fields for investor_id, startup_id, project_id, and a trigger_type
    that specifies the type of notification, such as 'project_follow' or 'startup_profile_update'.
    """
    investor_id = serializers.IntegerField(required=True)
    startup_id = serializers.IntegerField(required=True)
    project_id = serializers.IntegerField(required=True)
    trigger_type = serializers.ChoiceField(choices=[('project_follow', 'Project follow'), ('startup_profile_update', 'Startup profile update')], required=True)
