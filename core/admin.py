from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Music, Playlist, PlaylistItem, Rating, PlayHistory, Report, UserActivity, Genre, ContactMessage
from django.db import models

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('profile_image', 'bio')}),
    )

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        # Only allow changing the is_read status
        return True
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return []
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    actions = ['mark_as_read', 'mark_as_unread']

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'music_count', 'has_image')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(music_count=models.Count('music'))
        return queryset
    
    def music_count(self, obj):
        return obj.music_count
    
    def has_image(self, obj):
        if obj.image:
            return True
        return False
    
    has_image.boolean = True
    has_image.short_description = 'Has Image'
    music_count.short_description = 'Music Count'
    music_count.admin_order_field = 'music_count'

class MusicAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'get_genre', 'uploader', 'is_approved', 'plays_count')
    list_filter = ('genre_fk', 'is_approved', 'upload_date')
    search_fields = ('title', 'artist', 'album')
    autocomplete_fields = ['uploader']
    fields = ('title', 'artist', 'album', 'genre_fk', 'release_date', 'duration', 
              'audio_file', 'cover_image', 'is_approved', 'uploader')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['genre_fk'].widget.attrs['style'] = 'width: 400px;'
        return form
    
    def get_genre(self, obj):
        if obj.genre_fk:
            return obj.genre_fk.name
        return obj.genre or "-"
    
    get_genre.short_description = 'Genre'
    get_genre.admin_order_field = 'genre_fk'

    def save_model(self, request, obj, form, change):
        # When saving the model, also update the genre field for backward compatibility
        if obj.genre_fk:
            obj.genre = obj.genre_fk.name
        super().save_model(request, obj, form, change)

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at', 'is_public')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description')

class PlaylistItemAdmin(admin.ModelAdmin):
    list_display = ('playlist', 'music', 'order', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('playlist__name', 'music__title')

class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'music', 'rating', 'liked', 'created_at')
    list_filter = ('liked', 'created_at')
    search_fields = ('user__username', 'music__title')

class PlayHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'music', 'played_at', 'duration_played')
    list_filter = ('played_at',)
    search_fields = ('user__username', 'music__title')

class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'generated_by', 'generated_at')
    list_filter = ('generated_at',)
    search_fields = ('name', 'description')

class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'target_id', 'activity_date')
    list_filter = ('activity_type', 'activity_date')
    search_fields = ('user__username', 'activity_type')

admin.site.register(User, CustomUserAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Music, MusicAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(PlaylistItem, PlaylistItemAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(PlayHistory, PlayHistoryAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
