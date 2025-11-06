import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_username = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        # Crear nombre de sala único para dos usuarios
        usernames = sorted([self.user.username, self.other_username])
        self.room_name = 'chat_' + '_'.join(usernames)
        self.room_group_name = 'chat_' + self.room_name

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
        message = data['message']

        # Guardar mensaje en base de datos
        await self.save_message(self.user.username, self.other_username, message)

        # Enviar mensaje al grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
                'timestamp': data.get('timestamp', '')
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_message(self, sender_username, recipient_username, content):
        sender = User.objects.get(username=sender_username)
        recipient = User.objects.get(username=recipient_username)
        Message.objects.create(sender=sender, recipient=recipient, content=content)