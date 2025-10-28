from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    SeriesViewSet,
    WishlistViewSet,
    WatchlistViewSet,
    CommunityViewSet,
    MessageViewSet,
    PostViewSet,
    NotificationViewSet,
    CurrentlyWatchingViewSet,
    community_messages,
    register_user,
    login_user,
    logout_user,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'series', SeriesViewSet, basename='series')
router.register(r'wishlist', WishlistViewSet, basename='wishlist')  
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')
router.register(r'communities', CommunityViewSet, basename='communities')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'currently-watching', CurrentlyWatchingViewSet, basename='currently-watching')

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),

    # community messages endpoint
    path('communities/<int:community_id>/messages/', community_messages, name='community_messages'),

    path('', include(router.urls)),
]
