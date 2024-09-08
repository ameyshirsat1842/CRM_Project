import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from website.consumers import NotificationConsumer  # Updated with the correct app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CRMApp.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
        ])
    ),
})
