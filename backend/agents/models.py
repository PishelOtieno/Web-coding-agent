"""Agents app models."""
from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()


class Agent(models.Model):
    """AI Agent model for code generation and analysis."""
    PROJECT_STAGES = [
        ('analysis', 'Analysis'),
        ('design', 'Design'),
        ('development', 'Development'),
        ('review', 'Review'),
        ('deployment', 'Deployment'),
    ]
    
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='agent')
    name = models.CharField(max_length=255, default='AI Assistant')
    model_name = models.CharField(max_length=100, default='gpt-4')
    system_prompt = models.TextField(default='You are an expert coding assistant.')
    current_stage = models.CharField(max_length=50, choices=PROJECT_STAGES, default='analysis')
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=4000)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Agent - {self.project.name}"


class AgentCapability(models.Model):
    """Agent capabilities model."""
    CAPABILITY_TYPES = [
        ('read_file', 'Read File'),
        ('write_file', 'Write File'),
        ('create_file', 'Create File'),
        ('delete_file', 'Delete File'),
        ('search_files', 'Search Files'),
        ('execute_code', 'Execute Code'),
        ('generate_code', 'Generate Code'),
        ('analyze_code', 'Analyze Code'),
    ]
    
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='capabilities')
    capability = models.CharField(max_length=100, choices=CAPABILITY_TYPES)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ['agent', 'capability']

    def __str__(self):
        return f"{self.agent.project.name} - {self.capability}"
