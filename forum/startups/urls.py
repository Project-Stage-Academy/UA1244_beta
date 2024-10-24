from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartupViewSet, StartupListView, SendMessageView, StartupDetailView

router = DefaultRouter()
router.register(r'', StartupViewSet, basename='startup')

urlpatterns = [
    path('', include(router.urls)),
    path('list/', StartupListView.as_view(), name='startups-list'),
    path('message/', SendMessageView.as_view(), name='send_message'),
    path('<startup_id>/', StartupDetailView.as_view(), name='startup-detail'),
]
