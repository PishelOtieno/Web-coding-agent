"""Conversations app URLs."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

urlpatterns = [
    path('projects/<int:project_id>/conversations/', ConversationViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='conversation-list'),
    path('projects/<int:project_id>/conversations/<int:pk>/', ConversationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='conversation-detail'),
    path('projects/<int:project_id>/conversations/<int:pk>/send_message/', 
         ConversationViewSet.as_view({'post': 'send_message'}), name='send-message'),
]
