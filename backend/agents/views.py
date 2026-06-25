"""Agents app views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from projects.models import Project
from .models import Agent, AgentCapability
from .serializers import AgentSerializer, AgentDetailSerializer
from .llm_service import LLMFactory
from .workspace_tools import ProjectWorkspace, WorkspaceToolError


class AgentViewSet(viewsets.ModelViewSet):
    """Agent CRUD operations."""
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project = self.get_project()
        return Agent.objects.filter(project=project)

    def get_project(self):
        project = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        user = self.request.user
        if project.owner == user or project.collaborators.filter(user=user).exists():
            return project
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('You do not have access to this project.')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AgentDetailSerializer
        return AgentSerializer

    def perform_create(self, serializer):
        project = self.get_project()
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
        if not prompt:
            return Response({'prompt': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            llm = LLMFactory.create(
                provider=getattr(settings, 'LLM_PROVIDER', 'openai'),
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
    def read_file(self, request, pk=None, project_id=None):
        """Read a project file through the agent tool layer."""
        agent = self.get_object()
        path = request.data.get('path', '')
        workspace = ProjectWorkspace(agent.project, request.user)

        try:
            return Response(workspace.read_file(path))
        except WorkspaceToolError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def search_workspace(self, request, pk=None, project_id=None):
        """Search project file paths and contents."""
        agent = self.get_object()
        query = request.data.get('query', '')
        limit = int(request.data.get('limit', 20))
        workspace = ProjectWorkspace(agent.project, request.user)

        try:
            return Response(workspace.search(query, limit=min(max(limit, 1), 100)))
        except WorkspaceToolError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def propose_edit(self, request, pk=None, project_id=None):
        """Create a proposed full-file edit and unified diff without applying it."""
        agent = self.get_object()
        path = request.data.get('path', '')
        instructions = request.data.get('instructions', '')
        proposed_content = request.data.get('proposed_content')
        workspace = ProjectWorkspace(agent.project, request.user)

        try:
            current_file = workspace.read_file(path)
            if proposed_content is None:
                if not instructions:
                    return Response(
                        {'instructions': ['This field is required when proposed_content is omitted.']},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                proposed_content = self._generate_file_edit(agent, current_file, instructions)

            return Response(workspace.propose_edit(path, proposed_content, instructions))
        except WorkspaceToolError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def apply_edit(self, request, pk=None, project_id=None):
        """Apply an approved full-file edit to the project."""
        agent = self.get_object()
        path = request.data.get('path', '')
        proposed_content = request.data.get('proposed_content')
        expected_original_content = request.data.get('expected_original_content')
        change_description = request.data.get('change_description', 'Agent edit applied')

        if proposed_content is None:
            return Response({'proposed_content': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        workspace = ProjectWorkspace(agent.project, request.user)
        try:
            return Response(workspace.apply_edit(
                path=path,
                proposed_content=proposed_content,
                expected_original_content=expected_original_content,
                change_description=change_description,
            ))
        except WorkspaceToolError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_409_CONFLICT)

    def _generate_file_edit(self, agent, current_file, instructions: str) -> str:
        llm = LLMFactory.create(
            provider=getattr(settings, 'LLM_PROVIDER', 'openai'),
            model=agent.model_name,
            temperature=agent.temperature,
            max_tokens=agent.max_tokens,
        )
        messages = [
            {'role': 'system', 'content': (
                f'{agent.system_prompt}\n\n'
                'You are editing one file. Return only the complete updated file content. '
                'Do not wrap the response in Markdown fences and do not include commentary.'
            )},
            {'role': 'user', 'content': (
                f'Path: {current_file["path"]}\n'
                f'Language: {current_file["language"]}\n'
                f'Instructions: {instructions}\n\n'
                f'Current file content:\n{current_file["content"]}'
            )},
        ]
        return llm.generate(messages)

    @action(detail=True, methods=['post'])
    def stream_generate(self, request, pk=None, project_id=None):
        """Stream code generation from the agent."""
        agent = self.get_object()
        prompt = request.data.get('prompt', '')
        if not prompt:
            return Response({'prompt': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        
        def event_stream():
            try:
                llm = LLMFactory.create(
                    provider=getattr(settings, 'LLM_PROVIDER', 'openai'),
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
