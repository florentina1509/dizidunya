from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, permissions, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .serializers import (
    UserSerializer,
    SeriesSerializer,
    WishlistSerializer,
    WatchlistSerializer,
    CommunitySerializer,
    MessageSerializer,
    PostSerializer,
    NotificationSerializer,
    CurrentlyWatchingSerializer,
)
from .models import (
    Series,
    Wishlist,
    Watchlist,
    Community,
    Message,
    Post,
    Notification,
    CurrentlyWatching,
)

# -------------------------------
# USER VIEWSET
# -------------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# -------------------------------
# AUTHENTICATION (Register / Login / Logout)
# -------------------------------
@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    user = User(username=username, email=email)
    user.set_password(password)
    user.save()
    token, _ = Token.objects.get_or_create(user=user)

    return Response(
        {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            },
            "token": token.key,
        },
        status=201,
    )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)
    if not user:
        return Response({"error": "Invalid credentials"}, status=401)

    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            },
            "token": token.key,
        },
        status=200,
    )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def logout_user(request):
    if request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({"message": "Logged out successfully"}, status=200)
    return Response({"message": "No active session"}, status=200)


# -------------------------------
# SERIES VIEWSET
# -------------------------------
class SeriesViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.all().order_by("-id")
    serializer_class = SeriesSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        if user and user.is_staff:
            series = serializer.save(user=user)
            channel_layer = get_channel_layer()

            # Send to global group (for everyone)
            async_to_sync(channel_layer.group_send)(
                "notifications",
                {
                    "type": "send_notification",
                    "message": f"🎬 New Dizi added: {series.title} is now live on DiziDünya!",
                },
            )

            # Also send to all logged-in user channels (if any exist)
            for u in User.objects.all():
                async_to_sync(channel_layer.group_send)(
                    f"user_{u.id}",
                    {
                        "type": "send_notification",
                        "message": f"🎬 New Dizi added: {series.title} is now live on DiziDünya!",
                    },
                )

        else:
            return Response(
                {"error": "Only admins can add series."},
                status=status.HTTP_403_FORBIDDEN,
            )



# -------------------------------
# WISHLIST VIEWSET
# -------------------------------
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        series_id = request.data.get("series_id")
        if not series_id:
            return Response({"error": "series_id is required"}, status=400)
        try:
            series = Series.objects.get(id=series_id)
        except Series.DoesNotExist:
            return Response({"error": "Invalid series_id"}, status=404)

        wishlist_item, created = Wishlist.objects.get_or_create(user=user, series=series)
        if not created:
            return Response({"message": "This series is already in your wishlist."}, status=200)
        serializer = self.get_serializer(wishlist_item)
        return Response(serializer.data, status=201)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own wishlist items.")
        instance.delete()


# -------------------------------
# WATCHLIST VIEWSET
# -------------------------------
class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        series_id = request.data.get("series_id")
        if not series_id:
            return Response({"error": "series_id is required"}, status=400)
        try:
            series = Series.objects.get(id=series_id)
        except Series.DoesNotExist:
            return Response({"error": "Invalid series_id"}, status=404)

        watchlist_item, created = Watchlist.objects.get_or_create(user=user, series=series)
        if not created:
            return Response({"message": "This series is already in your watchlist."}, status=200)
        serializer = self.get_serializer(watchlist_item)
        return Response(serializer.data, status=201)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own watchlist items.")
        instance.delete()


# -------------------------------
# CURRENTLY WATCHING VIEWSET
# -------------------------------
class CurrentlyWatchingViewSet(viewsets.ModelViewSet):
    serializer_class = CurrentlyWatchingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CurrentlyWatching.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        series_id = request.data.get("series_id")

        if not series_id:
            return Response({"error": "series_id is required"}, status=400)

        try:
            series = Series.objects.get(id=series_id)
        except Series.DoesNotExist:
            return Response({"error": "Invalid series_id"}, status=404)

        watching_item, created = CurrentlyWatching.objects.get_or_create(user=user, series=series)
        if not created:
            return Response({"message": "Already in currently watching"}, status=200)

        serializer = self.get_serializer(watching_item)
        return Response(serializer.data, status=201)


# -------------------------------
# COMMUNITY VIEWSET (fixed leave)
# -------------------------------
class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all().order_by("-created_at")
    serializer_class = CommunitySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["language", "series__title"]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        community = serializer.save(created_by=user)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {
                "type": "send_notification",
                "message": f"💬 New community opened for {community.series.title} ({community.language})!",
            },
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        community = self.get_object()
        user = request.user

        if community.members.filter(id=user.id).exists():
            return Response({"message": "Already a member"}, status=200)

        community.members.add(user)
        Notification.objects.create(
            user=user,
            message=f"You joined {community.series.title} ({community.language}) community!",
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {
                "type": "send_notification",
                "message": f"👥 {user.username} joined {community.series.title} community!",
            },
        )

        return Response({"message": "Joined successfully"}, status=200)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticatedOrReadOnly])
    def leave(self, request, pk=None):
        community = self.get_object()
        user = request.user

        if not user.is_authenticated:
            return Response({"error": "Login required to leave this community."}, status=403)

        if not community.members.filter(id=user.id).exists():
            return Response({"message": "You are not a member of this community."}, status=400)

        community.members.remove(user)
        Notification.objects.create(
            user=user,
            message=f"You left {community.series.title} ({community.language}) community.",
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {
                "type": "send_notification",
                "message": f"👋 {user.username} left {community.series.title} community.",
            },
        )

        return Response({"message": "Left successfully"}, status=200)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        community = self.get_object()

        if not user.is_staff and not user.is_superuser:
            return Response({"error": "Only admins can delete communities."}, status=403)

        title = community.series.title
        community.delete()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {"type": "send_notification", "message": f"🗑 {title} community deleted by admin."},
        )
        return Response({"message": "Community deleted successfully."}, status=204)


# -------------------------------
# MESSAGE VIEWSET 
# -------------------------------
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by("created_at")
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(user=user)

    @action(detail=True, methods=["get"], url_path="messages", permission_classes=[AllowAny])
    def community_messages(self, request, pk=None):
        messages = Message.objects.filter(community_id=pk).order_by("created_at")
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


# -------------------------------
# POST VIEWSET
# -------------------------------
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        community_id = self.request.query_params.get("community_id")
        queryset = Post.objects.all()
        if community_id:
            queryset = queryset.filter(community_id=community_id)
        return queryset


# -------------------------------
# NOTIFICATION VIEWSET
# -------------------------------
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [permissions.AllowAny]
