from django.db import models
from django.contrib.auth.models import User

# -------------------------------
# SERIES MODEL
# -------------------------------
class Series(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    genre = models.CharField(max_length=100, blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='series_images/', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='series', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# -------------------------------
# WISHLIST MODEL
# -------------------------------
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist_items")
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name="wishlisted_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "series")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} → {self.series.title}"


# -------------------------------
# WATCHLIST MODEL
# -------------------------------
class Watchlist(models.Model):
    STATUS_CHOICES = [
        ('watching', 'Watching'),
        ('planned', 'Planned'),
        ('finished', 'Finished'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='watchlisted_by')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    notes = models.TextField(blank=True, null=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.series.title} ({self.status})"


# -------------------------------
# CURRENTLY WATCHING MODEL 
# -------------------------------
class CurrentlyWatching(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="currently_watching")
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name="current_viewers")
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "currently_watching"  
        unique_together = ("user", "series")

    def __str__(self):
        return f"{self.user.username} is currently watching {self.series.title}"


# -------------------------------
# COMMUNITY MODEL
# -------------------------------
class Community(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name="communities")
    language = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_communities")
    members = models.ManyToManyField(User, related_name="joined_communities", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.series.title} ({self.language})"


# -------------------------------
# MESSAGE MODEL
# -------------------------------
class Message(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"


# -------------------------------
# POST MODEL
# -------------------------------
class Post(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="posts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Post by {self.user.username} in {self.community.series.title}"


# -------------------------------
# NOTIFICATION MODEL
# -------------------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.message[:30]}"
