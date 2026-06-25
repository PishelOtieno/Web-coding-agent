"""Conversations app views."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from projects.models import Project
from .models import Conversation, Message
from .serializers import ConversationSerializer, ConversationDetailSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """Conversation CRUD operations."""
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        # Verify user has access to project
        if project.owner != self.request.user:
            if not project.collaborators.filter(user=self.request.user).exists():
                return Conversation.objects.none()
        return Conversation.objects.filter(project=project)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)
        serializer.save(project=project)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None, project_id=None):
        """Send a message in the conversation."""
        conversation = self.get_object()
        content = request.data.get('content')
        
        message = Message.objects.create(
            conversation=conversation,
            role='user',
            content=content
        )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Additional views for messages
class MessageViewSet(viewsets.ModelViewSet):
    """Message CRUD operations."""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_id')
        return Message.objects.filter(conversation_id=conversation_id)
