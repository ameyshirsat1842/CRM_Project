from channels.generic.websocket import AsyncWebsocketConsumer
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.group_name = None
        self.user_id = None

    async def connect(self):
        # Get the user's ID to create a group for user-specific notifications
        self.user_id = self.scope['user'].id
        self.group_name = f'notifications_{self.user_id}'

        # Join the user-specific group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group when the WebSocket disconnects
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Method to send notification to the WebSocket
    async def send_notification(self, event):
        # Retrieve message and link URL from the event
        message = event['message']
        link_url = event.get('link_url', '#')

        # Send notification to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'link_url': link_url
        }))
