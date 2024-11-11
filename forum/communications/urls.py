from django.urls import path

from communications.views import ConversationApiView, MessageApiView, ListMessagesApiView

app_name = 'communications'

urlpatterns = [
    path('api/conversations/', ConversationApiView.as_view(), name='conversation'),
    path('api/messages/', MessageApiView.as_view(), name='send_message'),
    path('api/conversations/<conversation_id>/messages', ListMessagesApiView.as_view(), name='list_messages'),
]