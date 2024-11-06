from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.registries import registry
from .models import Startup

startup_index = Index('startups')

@registry.register_document
class StartupDocument(Document):
    company_name = fields.TextField(
        attr='company_name',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    location = fields.ObjectField(
        attr='location',
        properties={
            'city': fields.TextField(),
            'country': fields.TextField(),
            'city_code': fields.TextField(),
        }
    )
    industries = fields.NestedField(
        properties={
            'name': fields.TextField(),
        }
    )
    number_of_employees = fields.IntegerField() 

    class Index:
        name = 'startups'

    class Django:
        model = Startup
        fields = [
            'required_funding',
            'funding_stage',
            'description',
            'total_funding',
            'website',
            'created_at',
        ]