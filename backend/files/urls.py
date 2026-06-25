"""Files app URLs."""
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FileViewSet

urlpatterns = [
    path('projects/<int:project_id>/files/', FileViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='file-list'),
    path('projects/<int:project_id>/files/tree/', FileViewSet.as_view({
        'get': 'tree',
    }), name='file-tree'),
    path('projects/<int:project_id>/files/<int:pk>/', FileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='file-detail'),
    path('projects/<int:project_id>/files/<int:pk>/versions/', FileViewSet.as_view({
        'get': 'versions',
    }), name='file-versions'),
    path('projects/<int:project_id>/files/<int:pk>/revert/', FileViewSet.as_view({
        'post': 'revert',
    }), name='file-revert'),
]
