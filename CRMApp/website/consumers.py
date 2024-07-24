import json
from channels.generic.websocket import WebsocketConsumer


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        # Code to handle WebSocket connection
        self.accept()

    def disconnect(self, close_code):
        # Code to handle WebSocket disconnection
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')

        # Send message back to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
