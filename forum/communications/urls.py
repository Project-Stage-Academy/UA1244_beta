from django.urls import path
from .api_view import SendMessageView

app_name = 'communications'

urlpatterns = [
    path('messages/send/<uuid:startup_id>/', SendMessageView.as_view(), name='send_message'),

]