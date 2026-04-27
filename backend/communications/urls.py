from django.urls import path

from .views import ConversationListCreateAPIView, MessageListCreateAPIView


urlpatterns = [
    path('conversations/', ConversationListCreateAPIView.as_view(), name='conversation-list-create'),
    path(
        'conversations/<int:pk>/messages/',
        MessageListCreateAPIView.as_view(),
        name='conversation-messages',
    ),
]
