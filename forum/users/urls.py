from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .api_view import UserViewSet, RegisterViewSet, ChangeActiveRoleAPIView, InvestorOnlyView, StartupOnlyView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'register', RegisterViewSet, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('change-role/', ChangeActiveRoleAPIView.as_view(), name='change-role'),
    path('investor-only/', InvestorOnlyView.as_view(), name='investor-only'),
    path('startup-only/', StartupOnlyView.as_view(), name='startup-only'),
    path('select-role/', views.select_role, name='select_role'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
]

