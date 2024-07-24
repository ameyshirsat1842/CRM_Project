import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import website.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CRMApp.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            website.routing.websocket_urlpatterns
        )
    ),
})
