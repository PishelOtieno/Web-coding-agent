"""Tasks app serializers."""
from rest_framework import serializers
from .models import Task, TaskAction


class TaskActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAction
        fields = ['id', 'action_type', 'target', 'input_data', 'output_data', 'status', 'error', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    actions = TaskActionSerializer(many=True, read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)

    class Meta:
        model = Task
        fields = ['id', 'project', 'conversation', 'title', 'description', 'status', 'priority',
                 'assigned_to', 'assigned_to_username', 'result', 'error_message', 'actions',
                 'created_at', 'started_at', 'completed_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskDetailSerializer(TaskSerializer):
    pass
