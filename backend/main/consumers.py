import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "notifications"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print("✅ WebSocket CONNECTED to notifications")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print("❌ WebSocket DISCONNECTED")

    async def receive(self, text_data=None, bytes_data=None):
        print(f"📩 Received message from client: {text_data}")

    async def send_notification(self, event):
        message = event.get("message", "")
        print(f"📢 Sending notification to client: {message}")
        await self.send(text_data=json.dumps({"message": message}))
