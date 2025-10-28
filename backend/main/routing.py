from django.urls import re_path
from main import consumers  # import from your main app

websocket_urlpatterns = [
    # Notifications WebSocket
    re_path(r"^ws/notifications/$", consumers.NotificationConsumer.as_asgi()),

    # Community Chat WebSocket (numeric ID)
    re_path(r"^ws/chat/(?P<community_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
]
