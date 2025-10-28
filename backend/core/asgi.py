import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import main.routing  

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# Django ASGI application
django_asgi_app = get_asgi_application()

# Main ASGI application (HTTP + WebSocket)
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(main.routing.websocket_urlpatterns)  
    ),
})
