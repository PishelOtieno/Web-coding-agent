"""Projects app views."""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, ProjectCollaborator
from .serializers import ProjectSerializer, ProjectDetailSerializer, ProjectCollaboratorSerializer
from .permissions import IsProjectOwnerOrCollaborator, IsProjectOwner


class ProjectViewSet(viewsets.ModelViewSet):
    """Project CRUD operations."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['language', 'is_public']
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            models.Q(owner=user) | models.Q(collaborators__user=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['add_collaborator', 'remove_collaborator']:
            return [IsAuthenticated(), IsProjectOwner()]
        return [permission() for permission in self.permission_classes]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_collaborator(self, request, pk=None):
        """Add a collaborator to the project."""
        project = self.get_object()
        self.check_object_permissions(request, project)
        
        username = request.data.get('username')
        role = request.data.get('role', 'editor')
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        collaborator, created = ProjectCollaborator.objects.get_or_create(
            project=project,
            user=user,
            defaults={'role': role}
        )
        
        if not created:
            collaborator.role = role
            collaborator.save()
        
        serializer = ProjectCollaboratorSerializer(collaborator)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def remove_collaborator(self, request, pk=None):
        """Remove a collaborator from the project."""
        project = self.get_object()
        self.check_object_permissions(request, project)
        
        user_id = request.data.get('user_id')
        try:
            collaborator = ProjectCollaborator.objects.get(project=project, user_id=user_id)
            collaborator.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProjectCollaborator.DoesNotExist:
            return Response({'error': 'Collaborator not found'}, status=status.HTTP_404_NOT_FOUND)
