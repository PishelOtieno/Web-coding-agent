"""Conversations app WebSocket consumer."""
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ConversationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time conversation."""
    
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'conversation_{self.conversation_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'conversation_message',
                'message': data.get('message'),
                'sender': data.get('sender'),
            }
        )

    async def conversation_message(self, event):
        """Handle messages from the group."""
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))
