from rest_framework import serializers
from django.contrib.auth.models import User
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
# SERIES SERIALIZER
# ======================================================
class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = [
            "id",
            "title",
            "description",
            "genre",
            "release_year",
            "image",
            "created_at",
        ]


# ======================================================
# WISHLIST SERIALIZER
# ======================================================
class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    series = SeriesSerializer(read_only=True)
    series_title = serializers.CharField(source="series.title", read_only=True)

    # For writing
    series_id = serializers.PrimaryKeyRelatedField(
        queryset=Series.objects.all(), source="series", write_only=True
    )

    class Meta:
        model = Wishlist
        fields = [
            "id",
            "user",
            "series",
            "series_title",
            "series_id",
            "added_at",
        ]


# ======================================================
# WATCHLIST SERIALIZER
# ======================================================
class WatchlistSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    series = SeriesSerializer(read_only=True)
    series_title = serializers.CharField(source="series.title", read_only=True)

    # For writing
    series_id = serializers.PrimaryKeyRelatedField(
        queryset=Series.objects.all(), source="series", write_only=True
    )

    class Meta:
        model = Watchlist
        fields = [
            "id",
            "user",
            "series",
            "series_title",
            "series_id",
            "status",
            "notes",
            "rating",
        ]


# ======================================================
# CURRENTLY WATCHING SERIALIZER
# ======================================================
class CurrentlyWatchingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    series = SeriesSerializer(read_only=True)
    series_title = serializers.CharField(source="series.title", read_only=True)

    series_id = serializers.PrimaryKeyRelatedField(
        queryset=Series.objects.all(), source="series", write_only=True
    )

    class Meta:
        model = CurrentlyWatching
        fields = [
            "id",
            "user",
            "series",
            "series_title",
            "series_id",
            "started_at",
        ]


# ======================================================
# COMMUNITY SERIALIZER
# ======================================================
class CommunitySerializer(serializers.ModelSerializer):
    series_title = serializers.CharField(source="series.title", read_only=True)
    series_image = serializers.ImageField(source="series.image", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    member_count = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # For creation
    series_id = serializers.PrimaryKeyRelatedField(
        queryset=Series.objects.all(), source="series", write_only=True
    )
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="created_by", write_only=True, required=False
    )

    def get_member_count(self, obj):
        return obj.members.count()

    class Meta:
        model = Community
        fields = [
            "id",
            "series_title",
            "series_image",
            "language",
            "created_by_name",
            "created_at",
            "member_count",
            "members",
            "series_id",
            "created_by_id",
        ]


# ======================================================
# MESSAGE SERIALIZER
# ======================================================
class MessageSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "community", "user", "user_name", "content", "created_at"]

    def get_user_name(self, obj):
        return obj.user.username if obj.user else "Deleted User"


# ======================================================
# POST SERIALIZER
# ======================================================
class PostSerializer(serializers.ModelSerializer):
    community_name = serializers.CharField(source="community.series.title", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)

    community_id = serializers.PrimaryKeyRelatedField(
        queryset=Community.objects.all(), source="community", write_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "community",
            "community_name",
            "user",
            "user_name",
            "content",
            "community_id",
            "user_id",
            "created_at",
        ]


# ======================================================
# USER SERIALIZER
# ======================================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "is_staff",
            "is_superuser",
        ]


# ======================================================
# NOTIFICATION SERIALIZER
# ======================================================
class NotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "user_name",
            "message",
            "is_read",
            "created_at",
        ]
