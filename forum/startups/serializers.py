from rest_framework import serializers
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .models import Startup, Industry
from projects.serializers import ProjectSerializer
from .document import StartupDocument

class StartupSerializer(serializers.ModelSerializer):
    """
    Serializer for the Startup model.
    This serializer validates and serializes the fields of the Startup model
    for creating and updating startup instances.
    """
    required_funding = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_funding = serializers.DecimalField(max_digits=10, decimal_places=2)

    projects = ProjectSerializer(many=True, read_only=True)
    class Meta:
        model = Startup
        fields = [
                'startup_id', 'user', 'company_name', 'required_funding', 
                'funding_stage', 'number_of_employees', 'location', 'industries', 'company_logo',
                'description', 'total_funding', 'website', 'created_at', 'projects' 
                ]

    def validate_company_name(self, value):
        
        #Validates that the company name is both present and unique Allows to update company name.
        
        if not value:
            raise serializers.ValidationError("Company name cannot be empty.")
        
        request = self.context.get('request')
        startup_id = self.instance.startup_id if self.instance else None
        existing_company = Startup.objects.filter(company_name=value)

        if request and request.method == 'PUT':
            if existing_company.exclude(startup_id=startup_id).exists():
                raise serializers.ValidationError("A company with this name already exists.")
        else:
            if existing_company.exists():
                raise serializers.ValidationError("A company with this name already exists.")

        return value

    def validate(self, data):
        """
        Validates that number of employees, total funding and required funding are positive values, 
        and ensures that required funding is greater than total funding.
        """
        total_funding = data.get('total_funding')
        required_funding = data.get('required_funding')
        number_of_employees = data.get('number_of_employees')
        
        if number_of_employees is not None and number_of_employees <= 0:
            raise serializers.ValidationError("Total funding must be a positive value.")
        if total_funding <= 0:
            raise serializers.ValidationError("Total funding must be a positive value.")
        if required_funding <= 0:
            raise serializers.ValidationError("Required funding must be a positive value.")

        if required_funding <= total_funding:
            raise serializers.ValidationError("Required funding must be greater than total funding.")

        return data
    
    def validate_description(self, value):
        """
        Validates that the description is not greater than 500 characters.
        """
        max_length = 500
        
        if len(value) > max_length:
            raise serializers.ValidationError(f"Description cannot exceed {max_length} characters.")
        return value


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = ['industry_id', 'name']

    def validate_name(self, value):
        if Industry.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("This industry name already exists (case-insensitive match).")
        return value
    

class StartupDocumentSerializer(DocumentSerializer):
    """
    Serializer for Startup Elasticsearch document.

    Provides JSON format for StartupDocument fields in API responses.
    """

    class Meta:
        document = StartupDocument  
        fields = [
            'company_name',
            'required_funding',
            'funding_stage',
            'number_of_employees',
            'description',
            'total_funding',
            'website',
            'created_at',
            'location',  
            'industries',  
        ]