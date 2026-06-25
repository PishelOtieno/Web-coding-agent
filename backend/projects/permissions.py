"""Projects app permissions."""
from rest_framework.permissions import BasePermission
from .models import Project


class IsProjectOwner(BasePermission):
    """Only project owner can perform this action."""
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsProjectOwnerOrCollaborator(BasePermission):
    """Only project owner or collaborator can perform this action."""
    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return obj.collaborators.filter(user=request.user).exists()
