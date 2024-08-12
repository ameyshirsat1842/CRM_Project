from channels.generic.websocket import AsyncWebsocketConsumer
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Handle disconnection
        pass

    async def receive(self, text_data):
        # Handle incoming messages if any
        pass

    async def send_notification(self, event):
        # Receive message from the group
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
