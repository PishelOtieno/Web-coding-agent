"""Files app serializers."""
from rest_framework import serializers
from .models import File, FileVersion


class FileVersionSerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = FileVersion
        fields = ['id', 'version_number', 'content', 'changed_by', 'changed_by_username', 'change_description', 'created_at']
        read_only_fields = ['id', 'version_number', 'created_at']


class FileSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ['id', 'project', 'name', 'path', 'file_type', 'language', 'size', 'is_directory', 
                 'parent', 'created_by', 'created_by_username', 'latest_version', 'created_at', 'updated_at']
        read_only_fields = ['id', 'project', 'created_by', 'created_at', 'updated_at']

    def get_latest_version(self, obj):
        version = obj.versions.first()
        if version:
            return FileVersionSerializer(version).data
        return None


class FileDetailSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    versions = FileVersionSerializer(many=True, read_only=True)

    class Meta:
        model = File
        fields = ['id', 'project', 'name', 'path', 'file_type', 'language', 'content', 'size', 
                 'is_directory', 'parent', 'created_by', 'created_by_username', 'versions', 'created_at', 'updated_at']
        read_only_fields = ['id', 'project', 'created_by', 'created_at', 'updated_at']
