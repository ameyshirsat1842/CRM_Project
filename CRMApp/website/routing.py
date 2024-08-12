from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from consumers import NotificationConsumer  # Adjust the import based on your app structure

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
        ])
    ),
})
