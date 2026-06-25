"""Agents app URLs."""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AgentViewSet

urlpatterns = [
    path('projects/<int:project_id>/agent/', AgentViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='agent-list'),
    path('projects/<int:project_id>/agent/<int:pk>/', AgentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
    }), name='agent-detail'),
    path('projects/<int:project_id>/agent/<int:pk>/generate/', AgentViewSet.as_view({
        'post': 'generate',
    }), name='agent-generate'),
    path('projects/<int:project_id>/agent/<int:pk>/stream/', AgentViewSet.as_view({
        'post': 'stream_generate',
    }), name='agent-stream'),
]
