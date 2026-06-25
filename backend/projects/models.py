"""Projects app models."""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    """Project model for organizing code and conversations."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    language = models.CharField(
        max_length=50,
        choices=[('python', 'Python'), ('javascript', 'JavaScript'), ('typescript', 'TypeScript'), ('other', 'Other')],
        default='python'
    )
    framework = models.CharField(max_length=100, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ['owner', 'name']

    def __str__(self):
        return f"{self.owner.username}/{self.name}"


class ProjectCollaborator(models.Model):
    """Collaborator model for project sharing."""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='editor')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['project', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"
