"""Agents app serializers."""
from rest_framework import serializers
from .models import Agent, AgentCapability


class AgentCapabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentCapability
        fields = ['id', 'capability', 'is_enabled']


class AgentSerializer(serializers.ModelSerializer):
    capabilities = AgentCapabilitySerializer(many=True, read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Agent
        fields = ['id', 'project', 'project_name', 'name', 'model_name', 'current_stage', 
                 'temperature', 'max_tokens', 'is_active', 'capabilities', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AgentDetailSerializer(AgentSerializer):
    system_prompt = serializers.CharField()
    config = serializers.JSONField()

    class Meta:
        model = Agent
        fields = ['id', 'project', 'project_name', 'name', 'model_name', 'system_prompt',
                 'current_stage', 'temperature', 'max_tokens', 'is_active', 'config', 
                 'capabilities', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
