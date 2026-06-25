"""Projects app serializers."""
from rest_framework import serializers
from .models import Project, ProjectCollaborator


class ProjectCollaboratorSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = ProjectCollaborator
        fields = ['id', 'user', 'user_info', 'role', 'added_at']
        read_only_fields = ['id', 'added_at']

    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
        }


class ProjectSerializer(serializers.ModelSerializer):
    collaborators = ProjectCollaboratorSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'owner', 'owner_username', 'name', 'description', 'language', 'framework', 
                 'is_public', 'tags', 'collaborators', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class ProjectDetailSerializer(ProjectSerializer):
    pass
