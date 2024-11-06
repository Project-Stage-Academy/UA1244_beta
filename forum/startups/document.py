from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.registries import registry
from .models import Startup

startup_index = Index('startups')
startup_index.settings(
    number_of_shards=1,
    number_of_replicas=1,
    refresh_interval='30s'
)

@registry.register_document
class StartupDocument(Document):
    """
    Elasticsearch document for the Startup model.
    Defines the fields and settings for indexing and searching startups.
    """
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
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "refresh_interval": "30s"
        }

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
