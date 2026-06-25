"""Files app views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from projects.models import Project
from .models import File, FileVersion
from .serializers import FileSerializer, FileDetailSerializer, FileVersionSerializer


class FileViewSet(viewsets.ModelViewSet):
    """File CRUD operations."""
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        project = self.get_project()
        return File.objects.filter(project=project)

    def get_project(self):
        project = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        user = self.request.user
        if project.owner == user or project.collaborators.filter(user=user).exists():
            return project
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('You do not have access to this project.')

    def get_serializer_class(self):
        if self.action in ['create', 'retrieve', 'update', 'partial_update']:
            return FileDetailSerializer
        return FileSerializer

    def perform_create(self, serializer):
        project = self.get_project()
        serializer.save(project=project, created_by=self.request.user)

    def perform_update(self, serializer):
        file = serializer.save()
        # Create a new version on update
        latest_version = file.versions.first()
        version_number = (latest_version.version_number + 1) if latest_version else 1
        
        FileVersion.objects.create(
            file=file,
            version_number=version_number,
            content=file.content,
            changed_by=self.request.user,
            change_description='File updated'
        )

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None, project_id=None):
        """Get file version history."""
        file = self.get_object()
        versions = file.versions.all()
        serializer = FileVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def revert(self, request, pk=None, project_id=None):
        """Revert file to a specific version."""
        file = self.get_object()
        version_id = request.data.get('version_id')
        
        try:
            version = FileVersion.objects.get(id=version_id, file=file)
            file.content = version.content
            file.save()
            
            FileVersion.objects.create(
                file=file,
                version_number=file.versions.first().version_number + 1,
                content=file.content,
                changed_by=request.user,
                change_description=f'Reverted to version {version.version_number}'
            )
            
            serializer = FileDetailSerializer(file)
            return Response(serializer.data)
        except FileVersion.DoesNotExist:
            return Response({'error': 'Version not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def tree(self, request, project_id=None):
        """Get file tree structure."""
        project = self.get_project()
        root_files = File.objects.filter(project=project, parent__isnull=True)
        serializer = FileSerializer(root_files, many=True)
        return Response(serializer.data)
