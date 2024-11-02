from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StartupViewSet,
    StartupListView,
    SendMessageView,
    StartupDetailView,
    SavedStartupsListAPIView,
    UnfollowStartupAPIView,
    get_industries_bulk
)

router = DefaultRouter()
router.register(r'', StartupViewSet, basename='startup')

urlpatterns = [
    path('', include(router.urls)),
    path('', StartupListView.as_view(), name='startups-list'),
    path('message/', SendMessageView.as_view(), name='send_message'),
    path('<startup_id>/', StartupDetailView.as_view(), name='startup-detail'),
    path('api/v1/investor/saved-startups/', SavedStartupsListAPIView.as_view(), name='saved_startups_list'),
    path('api/v1/startups/<uuid:startup_id>/unsave/', UnfollowStartupAPIView.as_view(), name='unfollow_startup'),
    path('industries/bulk/', get_industries_bulk, name='industries_bulk'),
]

