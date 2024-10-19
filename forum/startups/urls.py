from django.urls import path
from .views import StartupListView, SendMessageView, StartupDetailView

urlpatterns = [
    path('list/', StartupListView.as_view(), name='startups-list'),
    path('message/', SendMessageView.as_view(), name='send_message'),
    path('<startup_id>/', StartupDetailView.as_view(), name='startup-detail'),

]