from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, permissions, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
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

# ======================================================
# SAFE TOKEN AUTHENTICATION
# ======================================================
class SafeTokenAuthentication(TokenAuthentication):
    """Prevents logout if token missing or invalid."""
    def authenticate(self, request):
        try:
            auth = super().authenticate(request)
            if not auth:
                return None
            return auth
        except Exception:
            return None


# ======================================================
# CUSTOM PERMISSIONS
# ======================================================
class IsAdminOrReadOnly(permissions.BasePermission):
    """Only admin/staff can modify data; everyone can view."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and (request.user.is_staff or request.user.is_superuser)


# ======================================================
# USER VIEWSET
# ======================================================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# ======================================================
# AUTHENTICATION
# ======================================================
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

    user = User.objects.create_user(username=username, email=email, password=password)
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


# ======================================================
# SERIES VIEWSET — Only Admins Can Modify
# ======================================================
class SeriesViewSet(viewsets.ModelViewSet):
    authentication_classes = [SafeTokenAuthentication]
    queryset = Series.objects.all().order_by("-id")
    serializer_class = SeriesSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description"]

    def perform_create(self, serializer):
        series = serializer.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",
            {"type": "send_notification", "message": f"New Dizi added: {series.title}"},
        )


# ======================================================
# WISHLIST VIEWSET
# ======================================================
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        series_id = request.data.get("series_id")
        if not series_id:
            return Response({"error": "series_id is required"}, status=400)
        try:
            series = Series.objects.get(id=series_id)
        except Series.DoesNotExist:
            return Response({"error": "Invalid series_id"}, status=404)
        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, series=series)
        if not created:
            return Response({"message": "Already in wishlist"}, status=200)
        return Response(self.get_serializer(wishlist_item).data, status=201)


# ======================================================
# WATCHLIST VIEWSET
# ======================================================
class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        series_id = request.data.get("series_id")
        if not series_id:
            return Response({"error": "series_id is required"}, status=400)
        try:
            series = Series.objects.get(id=series_id)
        except Series.DoesNotExist:
            return Response({"error": "Invalid series_id"}, status=404)
        watchlist_item, created = Watchlist.objects.get_or_create(user=request.user, series=series)
        if not created:
            return Response({"message": "Already in watchlist"}, status=200)
        return Response(self.get_serializer(watchlist_item).data, status=201)


# ======================================================
# CURRENTLY WATCHING VIEWSET
# ======================================================
class CurrentlyWatchingViewSet(viewsets.ModelViewSet):
    serializer_class = CurrentlyWatchingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CurrentlyWatching.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        series_id = request.data.get("series_id")
        if not series_id:
            return Response({"error": "series_id is required"}, status=400)
        try:
            series = Series.objects.get(id=series_id)
        except Series.DoesNotExist:
            return Response({"error": "Invalid series_id"}, status=404)
        watching_item, created = CurrentlyWatching.objects.get_or_create(user=request.user, series=series)
        if not created:
            return Response({"message": "Already watching"}, status=200)
        return Response(self.get_serializer(watching_item).data, status=201)


# ======================================================
# COMMUNITY VIEWSET
# ======================================================
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
                "message": f"New community opened for {community.series.title} ({community.language})!",
            },
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        community = self.get_object()
        user = request.user
        if community.members.filter(id=user.id).exists():
            return Response({"message": "Already a member"}, status=200)
        community.members.add(user)
        Notification.objects.create(user=user, message=f"You joined {community.series.title} community!")
        return Response({"message": "Joined successfully"}, status=200)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def leave(self, request, pk=None):
        community = self.get_object()
        user = request.user
        if not community.members.filter(id=user.id).exists():
            return Response({"message": "Not a member"}, status=400)
        community.members.remove(user)
        Notification.objects.create(user=user, message=f"You left {community.series.title} community.")
        return Response({"message": "Left successfully"}, status=200)


# ======================================================
# MESSAGE VIEWSET + COMMUNITY MESSAGES ENDPOINT
# ======================================================
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by("created_at")
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(user=user)


@api_view(["GET"])
@permission_classes([AllowAny])
def community_messages(request, community_id):
    if not Community.objects.filter(id=community_id).exists():
        return Response({"error": "Community not found"}, status=404)
    messages = Message.objects.filter(community_id=community_id).order_by("created_at")
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data, status=200)


# ======================================================
# POST VIEWSET
# ======================================================
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]


# ======================================================
# NOTIFICATION VIEWSET
# ======================================================
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]
