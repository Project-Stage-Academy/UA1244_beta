"""
URL configuration for forum project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from users.api_view import ActivateAccountView, SignOutView



urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    # Application URLs
    path("api/v1/", include("users.urls")),
    path("projects/", include("projects.urls")),
    path("profiles/", include("profiles.urls")),
    path("communications/", include("communications.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("investors/", include("investors.urls")),
    path("startups/", include("startups.urls")),

    # JWT Token URLs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),  

    # Authentication URLs (using Djoser)
    path('api/v1/auth/', include('djoser.urls')),       
    path('api/v1/auth/', include('djoser.urls.jwt')),

    path('activate/<str:token>/', ActivateAccountView.as_view(), name='activate'),
    
    # Logout URL
    path('api/v1/logout/', SignOutView.as_view(), name='logout'),
]
