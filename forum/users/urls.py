from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .api_view import UserViewSet, RegisterViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'register', RegisterViewSet, basename='register')

urlpatterns = [
    path("users/list", views.users, name="users"),
    path('', include(router.urls)),
]
