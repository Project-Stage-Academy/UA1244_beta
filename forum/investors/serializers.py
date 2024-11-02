from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.

    This serializer handles the conversion of Notification model instances 
    into JSON format for API responses and validates incoming data for 
    Notification creation and updates.

    Fields:
        All fields from the Notification model are included, as specified 
        by `fields = '__all__'`.
    
    Meta:
        model (Notification): The model that this serializer serializes.
        fields (str): Specifies that all fields of the Notification model 
                      are included in the serialized output.
    """ 
    class Meta:
        model = Notification
        fields = '__all__'
