import json
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from main.models import Message, Community


# -------------------------------
# 📢 Notification Consumer
# -------------------------------
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connect all clients to a single 'notifications' group."""
        self.group_name = "notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print("✅ WebSocket connected to notifications group")

        # Optional: send welcome message
        await self.send(text_data=json.dumps({
            "message": "Connected to DiziDunya notifications 🎬"
        }))

    async def disconnect(self, close_code):
        """Remove client from the notifications group."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print("❌ WebSocket disconnected from notifications group")

    async def receive(self, text_data):
        """Handle incoming messages (if frontend ever sends)."""
        try:
            data = json.loads(text_data)
            message = data.get("message", "No message content")
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "send_notification",
                    "message": message,
                },
            )
        except Exception as e:
            print("⚠️ Error receiving WebSocket data:", e)

    async def send_notification(self, event):
        """Send a message to all connected clients."""
        message = event.get("message", "")
        await self.send(text_data=json.dumps({"message": message}))


# -------------------------------
# 💬 Chat Consumer (Community Chat)
# -------------------------------
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Join a specific community chat room."""
        self.community_id = self.scope["url_route"]["kwargs"]["community_id"]
        self.room_group_name = f"chat_{self.community_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"✅ Joined chat room: {self.room_group_name}")

    async def disconnect(self, close_code):
        """Leave the chat room."""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"❌ Left chat room: {self.room_group_name}")

    async def receive(self, text_data):
        """Handle incoming messages from clients."""
        try:
            data = json.loads(text_data)
            message_text = data.get("message", "")
            username = data.get("username", "Unknown User")
            user_id = data.get("user_id")

            if message_text.strip():
                await self.save_message(self.community_id, user_id, message_text)

                # Broadcast message to all clients in the same room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message_text,
                        "username": username,
                        "timestamp": datetime.now().strftime("%H:%M"),
                    },
                )
        except Exception as e:
            print("⚠️ Error handling chat message:", e)

    async def chat_message(self, event):
        """Send message to WebSocket clients."""
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event.get("username", "Unknown User"),
            "timestamp": event.get("timestamp", ""),
        }))

    @sync_to_async
    def save_message(self, community_id, user_id, content):
        """Save messages to the database asynchronously."""
        try:
            community = Community.objects.filter(id=community_id).first()
            user = User.objects.filter(id=user_id).first()
            if community and user:
                Message.objects.create(community=community, user=user, content=content)
        except Exception as e:
            print("⚠️ Error saving message:", e)
