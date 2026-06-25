"""Conversations app routing for WebSocket."""
from django.urls import path
from .consumers import ConversationConsumer

websocket_urlpatterns = [
    path('ws/conversation/<int:conversation_id>/', ConversationConsumer.as_asgi()),
]
