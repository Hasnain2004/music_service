from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import json

class User(AbstractUser):
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='genre_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Music(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    genre_fk = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='music')
    release_date = models.DateField(blank=True, null=True)
    duration = models.FloatField(default=0.0)
    audio_file = models.FileField(upload_to='music/')
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    upload_date = models.DateTimeField(default=timezone.now)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_music')
    is_approved = models.BooleanField(default=True)
    plays_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.artist}"

class Playlist(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    cover_image = models.ImageField(upload_to='playlist_covers/', blank=True, null=True)

    def __str__(self):
        return self.name

class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='items')
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    added_at = models.DateTimeField(default=timezone.now)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ['playlist', 'music']

    def __str__(self):
        return f"{self.playlist.name} - {self.music.title}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    music = models.ForeignKey(Music, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(default=0)
    liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['user', 'music']

    def __str__(self):
        return f"{self.user.username} - {self.music.title} - {self.rating}"

class PlayHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='play_history')
    music = models.ForeignKey(Music, on_delete=models.CASCADE)
    played_at = models.DateTimeField(default=timezone.now)
    duration_played = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.music.title} - {self.played_at}"

class Report(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    generated_at = models.DateTimeField(default=timezone.now)
    data = models.TextField()  # Storing JSON as text
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')

    def set_data(self, data_dict):
        self.data = json.dumps(data_dict)

    def get_data(self):
        return json.loads(self.data)

    def __str__(self):
        return self.name

class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('PLAY', 'Play'),
        ('LIKE', 'Like'),
        ('RATE', 'Rate'),
        ('COMMENT', 'Comment'),
        ('CREATE_PLAYLIST', 'Create Playlist'),
        ('ADD_TO_PLAYLIST', 'Add to Playlist'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    target_id = models.IntegerField()  # ID of the target object (music, playlist, etc.)
    activity_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.activity_date}"
