from django.contrib import admin
from .models import Song, Rating, UserSession, UserProfile, ContactMessage

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'release_date', 'created_at')
    list_filter = ('genre', 'is_active', 'created_at')
    search_fields = ('title', 'artist', 'album')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'song__title')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'last_played')
    list_filter = ('last_played',)
    search_fields = ('user__username', 'song__title')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_photo')
    search_fields = ('user__username',)

admin.site.register(ContactMessage)
