from django.urls import path
from .views import SaveStartupView, InvestorNotificationsAPIView

urlpatterns = [
    path('api/v1/<uuid:startup_id>/save/', SaveStartupView.as_view(), name='save_startup'),
    path('api/v1/notifications/', InvestorNotificationsAPIView.as_view(), name='investor_notifications'),
]
