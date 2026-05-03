from django.urls import path

from .views import ChatUserListAPIView, ConversationListCreateAPIView, MessageListCreateAPIView


urlpatterns = [
    path('users/', ChatUserListAPIView.as_view(), name='chat-users'),
    path('conversations/', ConversationListCreateAPIView.as_view(), name='conversation-list-create'),
    path(
        'conversations/<int:pk>/messages/',
        MessageListCreateAPIView.as_view(),
        name='conversation-messages',
    ),
]
