from rest_framework import serializers
from .models import Startup

class StartupSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Startup model.

    This serializer converts the Startup model instance into a format suitable for 
    JSON rendering, and vice versa. It includes all fields from the Startup model 
    using the `fields = '__all__'` declaration, which means all model fields 
    will be included in the serialized data.

    The `ModelSerializer` class automatically handles creating, updating, and validating 
    Startup instances based on the provided data, simplifying the process of interacting 
    with the API.

    Meta attributes:
        model: Specifies the `Startup` model to serialize.
        fields: Specifies that all fields from the `Startup` model will be serialized.
    """
    class Meta:
        model = Startup
        fields = '__all__'