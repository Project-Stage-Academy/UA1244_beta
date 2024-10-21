from django.urls import path
from .views import SaveStartupView

urlpatterns = [
    path('api/v1/<uuid:startup_id>/save/', SaveStartupView.as_view(), name='save_startup'),
]
