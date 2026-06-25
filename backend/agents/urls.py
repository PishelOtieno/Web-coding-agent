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
    path('projects/<int:project_id>/agent/<int:pk>/read_file/', AgentViewSet.as_view({
        'post': 'read_file',
    }), name='agent-read-file'),
    path('projects/<int:project_id>/agent/<int:pk>/search_workspace/', AgentViewSet.as_view({
        'post': 'search_workspace',
    }), name='agent-search-workspace'),
    path('projects/<int:project_id>/agent/<int:pk>/propose_edit/', AgentViewSet.as_view({
        'post': 'propose_edit',
    }), name='agent-propose-edit'),
    path('projects/<int:project_id>/agent/<int:pk>/apply_edit/', AgentViewSet.as_view({
        'post': 'apply_edit',
    }), name='agent-apply-edit'),
    path('projects/<int:project_id>/agent/<int:pk>/stream/', AgentViewSet.as_view({
        'post': 'stream_generate',
    }), name='agent-stream'),
]
