"""Files app models."""
from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()


class File(models.Model):
    """File model for project file management."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=1000)
    file_type = models.CharField(max_length=50)
    language = models.CharField(max_length=50, blank=True, null=True)
    content = models.TextField()
    size = models.IntegerField()
    is_directory = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_files')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['path']
        unique_together = ['project', 'path']

    def __str__(self):
        return f"{self.project.name}/{self.path}"


class FileVersion(models.Model):
    """File version model for tracking changes."""
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    content = models.TextField()
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ['file', 'version_number']

    def __str__(self):
        return f"{self.file.name} v{self.version_number}"
