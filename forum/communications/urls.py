from django.urls import path

from communications.views import ConversationApiView, MessageApiView, ListMessagesApiView

app_name = 'communications'

urlpatterns = [
    path('api/conversations/', ConversationApiView.as_view()),
    path('api/messages/', MessageApiView.as_view()),
    path('api/conversations/<conversation_id>/messages', ListMessagesApiView.as_view()),
]