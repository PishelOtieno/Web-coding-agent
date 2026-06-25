"""Tasks app URLs."""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskActionViewSet

urlpatterns = [
    path('projects/<int:project_id>/tasks/', TaskViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='task-list'),
    path('projects/<int:project_id>/tasks/<int:pk>/', TaskViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='task-detail'),
    path('projects/<int:project_id>/tasks/<int:pk>/start/', TaskViewSet.as_view({
        'post': 'start',
    }), name='task-start'),
    path('projects/<int:project_id>/tasks/<int:pk>/complete/', TaskViewSet.as_view({
        'post': 'complete',
    }), name='task-complete'),
    path('projects/<int:project_id>/tasks/<int:pk>/fail/', TaskViewSet.as_view({
        'post': 'fail',
    }), name='task-fail'),
    path('projects/<int:project_id>/tasks/<int:pk>/actions/', TaskViewSet.as_view({
        'get': 'actions',
    }), name='task-actions'),
]
