from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.registries import registry
from .models import Project

project_index = Index('projects')
project_index.settings(
    number_of_shards=1,
    number_of_replicas=1,
    refresh_interval='30s'
)

@registry.register_document
class ProjectDocument(Document):
    """
    Elasticsearch document for the Project model.
    Defines the fields and settings for indexing and searching projects.
    """
    title = fields.TextField(
        attr='title',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )
    startup = fields.ObjectField(
        attr='startup',
        properties={
            'startup_id': fields.KeywordField(),
            'company_name': fields.TextField(
                attr='company_name',
                fields={
                    'raw': fields.KeywordField(),
                }
            ),
            'funding_stage': fields.TextField(),
        }
    )
    industry = fields.TextField(
        attr='industry',
        fields={
            'raw': fields.KeywordField(),
        }
    )

    class Index:
        name = 'projects'
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "refresh_interval": "30s"
        }

    class Django:
        model = Project
        fields = [
            'description',
            'required_amount',
            'status',
            'planned_start_date',
            'actual_start_date',
            'planned_finish_date',
            'actual_finish_date',
            'created_at',
            'last_update',
        ]
