"""
URL routing for the users application.

Defines the endpoints for user-related operations, including:
    - User registration, retrieval, and updates
    - Role-based access endpoints (investor-only, startup-only)
    - User login and role change functionality
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_view import (
    UserViewSet,
    RegisterViewSet,
    ChangeActiveRoleAPIView,
    InvestorOnlyView,
    StartupOnlyView,
    LoginAPIView,
    UserUpdateView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'register', RegisterViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('change-role/', ChangeActiveRoleAPIView.as_view(), name='change-role'),
    path('investor-only/', InvestorOnlyView.as_view(), name='investor-only'),
    path('startup-only/', StartupOnlyView.as_view(), name='startup-only'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('user/update/', UserUpdateView.as_view(), name='user_update'),
]
