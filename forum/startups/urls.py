from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartupViewSet

router = DefaultRouter()
router.register(r'', StartupViewSet, basename='startup')

urlpatterns = [
    path('', include(router.urls)),
]