"""Agents app views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from projects.models import Project
from .models import Agent, AgentCapability
from .serializers import AgentSerializer, AgentDetailSerializer
from .llm_service import LLMFactory


class AgentViewSet(viewsets.ModelViewSet):
    """Agent CRUD operations."""
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        return Agent.objects.filter(project=project)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AgentDetailSerializer
        return AgentSerializer

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        agent = serializer.save(project=project)
        
        # Initialize default capabilities
        default_capabilities = [
            'read_file', 'write_file', 'create_file', 'search_files',
            'generate_code', 'analyze_code'
        ]
        for capability in default_capabilities:
            AgentCapability.objects.get_or_create(
                agent=agent,
                capability=capability,
                defaults={'is_enabled': True}
            )

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None, project_id=None):
        """Generate code using the agent."""
        agent = self.get_object()
        prompt = request.data.get('prompt', '')
        
        try:
            llm = LLMFactory.create(
                provider=agent.model_name.split('-')[0].lower() if '-' in agent.model_name else 'openai',
                model=agent.model_name,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens
            )
            
            messages = [
                {'role': 'system', 'content': agent.system_prompt},
                {'role': 'user', 'content': prompt}
            ]
            
            response = llm.generate(messages)
            
            return Response({
                'response': response,
                'model': agent.model_name,
                'timestamp': str(__import__('django.utils.timezone', fromlist=['now']).now())
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def stream_generate(self, request, pk=None, project_id=None):
        """Stream code generation from the agent."""
        agent = self.get_object()
        prompt = request.data.get('prompt', '')
        
        def event_stream():
            try:
                llm = LLMFactory.create(
                    provider='openai',
                    model=agent.model_name,
                    temperature=agent.temperature,
                    max_tokens=agent.max_tokens
                )
                
                messages = [
                    {'role': 'system', 'content': agent.system_prompt},
                    {'role': 'user', 'content': prompt}
                ]
                
                for chunk in llm.stream(messages):
                    yield f"data: {chunk}\n\n"
            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        
        from django.http import StreamingHttpResponse
        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
