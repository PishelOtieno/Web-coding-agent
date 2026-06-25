"""Conversations app views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from projects.models import Project
from .models import Conversation, Message
from .serializers import ConversationSerializer, ConversationDetailSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """Conversation CRUD operations."""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project = self.get_project()
        return Conversation.objects.filter(project=project)

    def get_project(self):
        project = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        user = self.request.user
        if project.owner == user or project.collaborators.filter(user=user).exists():
            return project
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied('You do not have access to this project.')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        project = self.get_project()
        serializer.save(project=project)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None, project_id=None):
        """Send a message in the conversation."""
        conversation = self.get_object()
        content = request.data.get('content')
        if not content:
            return Response({'content': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        
        user_message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=content
        )

        assistant_message = None
        assistant_error = None
        api_key = getattr(settings, 'OPENAI_API_KEY', '')

        if api_key:
            try:
                from agents.llm_service import LLMFactory

                agent = getattr(conversation.project, 'agent', None)
                system_prompt = agent.system_prompt if agent else 'You are an expert coding assistant.'
                model_name = agent.model_name if agent else getattr(settings, 'OPENAI_MODEL', 'gpt-4')
                temperature = agent.temperature if agent else 0.7
                max_tokens = agent.max_tokens if agent else 4000

                history = [
                    {'role': msg.role, 'content': msg.content}
                    for msg in conversation.messages.exclude(role='system').order_by('created_at')[:20]
                ]
                messages = [{'role': 'system', 'content': system_prompt}, *history]
                llm = LLMFactory.create(
                    provider=getattr(settings, 'LLM_PROVIDER', 'openai'),
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                response_text = llm.generate(messages)
                assistant_message = Message.objects.create(
                    conversation=conversation,
                    role='assistant',
                    content=response_text
                )
            except Exception as exc:
                assistant_error = str(exc)
        else:
            assistant_error = 'AI generation is not configured. Set OPENAI_API_KEY to enable assistant replies.'

        return Response({
            'user_message': MessageSerializer(user_message).data,
            'assistant_message': MessageSerializer(assistant_message).data if assistant_message else None,
            'assistant_error': assistant_error,
        }, status=status.HTTP_201_CREATED)


# Additional views for messages
class MessageViewSet(viewsets.ModelViewSet):
    """Message CRUD operations."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        return Message.objects.filter(conversation_id=conversation_id)
