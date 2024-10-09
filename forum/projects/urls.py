from django.urls import path
from . import views

urlpatterns = [
        path('<uuid:project_id>/history/', views.project_history_view, name='project_history'),
        path('api/', views.ProjectListCreateView.as_view(), name='project-list-create'),
]
