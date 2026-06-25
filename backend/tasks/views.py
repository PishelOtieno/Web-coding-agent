"""Tasks app views."""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from projects.models import Project
from .models import Task, TaskAction
from .serializers import TaskSerializer, TaskDetailSerializer, TaskActionSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """Task CRUD operations."""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'priority']
    search_fields = ['title', 'description']

    def get_queryset(self):
        project = self.get_project()
        return Task.objects.filter(project=project)

    def get_project(self):
        project = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        user = self.request.user
        if project.owner == user or project.collaborators.filter(user=user).exists():
            return project
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('You do not have access to this project.')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        project = self.get_project()
        serializer.save(project=project)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None, project_id=None):
        """Start a task."""
        task = self.get_object()
        from django.utils import timezone
        task.status = 'in_progress'
        task.started_at = timezone.now()
        task.save()
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None, project_id=None):
        """Complete a task."""
        task = self.get_object()
        from django.utils import timezone
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.result = request.data.get('result', {})
        task.save()
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None, project_id=None):
        """Mark a task as failed."""
        task = self.get_object()
        task.status = 'failed'
        task.error_message = request.data.get('error', '')
        task.save()
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def actions(self, request, pk=None, project_id=None):
        """Get task actions."""
        task = self.get_object()
        actions = task.actions.all()
        serializer = TaskActionSerializer(actions, many=True)
        return Response(serializer.data)


class TaskActionViewSet(viewsets.ModelViewSet):
    """Task action operations."""
    queryset = TaskAction.objects.all()
    serializer_class = TaskActionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return TaskAction.objects.filter(task_id=task_id)
