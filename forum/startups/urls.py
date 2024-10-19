from django.urls import path, include
from .views import StartupListView, SendMessageView

urlpatterns = [
    path('api/startups/', StartupListView.as_view(), name='startups_list'),
    path('api/startups/message/', SendMessageView.as_view(), name='send_message'),

]