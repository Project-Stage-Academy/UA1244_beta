from django.urls import path
from .views import (
    StartupListView,
    SendMessageView,
    StartupDetailView,
    SavedStartupsListAPIView,
    UnfollowStartupAPIView,
)

urlpatterns = [
    path('list/', StartupListView.as_view(), name='startups-list'),
    path('message/', SendMessageView.as_view(), name='send_message'),
    path('<startup_id>/', StartupDetailView.as_view(), name='startup-detail'),
    path('api/v1/investor/saved-startups/', SavedStartupsListAPIView.as_view(), name='saved_startups_list'),
    path('api/v1/startups/<uuid:startup_id>/unsave/', UnfollowStartupAPIView.as_view(), name='unfollow_startup'),
]
