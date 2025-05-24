from django import forms
from .models import User, Music, Playlist, Genre

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio', 'profile_image']

class MusicForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ['title', 'artist', 'album', 'genre', 'genre_fk', 'audio_file', 'cover_image', 'is_approved']

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'is_public', 'cover_image']

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'description', 'image']