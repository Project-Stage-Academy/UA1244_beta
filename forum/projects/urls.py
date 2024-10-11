from django.urls import path
from . import views

urlpatterns = [
        path('api/v1/history/<uuid:project_id>/', views.project_history_view, name='project-history'),
        path('api/v1/management/', views.ProjectListCreateView.as_view(), name='project-management'),
]
