from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Avg, Max
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from .models import User, Music, Playlist, PlaylistItem, Rating, PlayHistory, UserActivity, Genre, ContactMessage
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.urls import resolve, reverse
import json
import os
import uuid
from datetime import timedelta
from .forms import *

# Custom middleware to handle login redirects
class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Public URLs that don't require authentication
        self.public_urls = [
            'login',
            'register',
            'about',
            'contact',
            'logout',
        ]

    def __call__(self, request):
        if not request.user.is_authenticated:
            current_url = resolve(request.path_info).url_name
            
            # Allow access to public URLs
            if current_url in self.public_urls:
                return self.get_response(request)
                
            # Allow access to static files and media
            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                return self.get_response(request)
                
            # Redirect to login for all other URLs
            return redirect(f"{reverse('login')}?next={request.path}")
            
        return self.get_response(request)

@login_required
def index(request):
    """View for the home page"""
    # Get latest music
    latest_music = Music.objects.filter(is_approved=True).order_by('-upload_date')[:8]
    
    # Get popular music (most played)
    popular_music = Music.objects.filter(is_approved=True).order_by('-plays_count')[:8]
    
    # Get all genres
    genres = Genre.objects.all()[:8]
    
    # Get active uploaders (users with most uploads)
    active_uploaders = User.objects.annotate(
        upload_count=Count('uploaded_music')
    ).filter(upload_count__gt=0).order_by('-upload_count')[:4]
    
    context = {
        'latest_music': latest_music,
        'popular_music': popular_music,
        'genres': genres,
        'active_uploaders': active_uploaders
    }
    
    return render(request, 'core/index.html', context)

def about(request):
    """View for the about page"""
    return render(request, 'core/about.html')

def contact(request):
    """View for the contact page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            # Save the message to the database
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            
            # Optional: Send email notification
            # send_mail(
            #     f'New Contact Message: {subject}',
            #     f'From: {name} ({email})\n\n{message}',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [settings.ADMIN_EMAIL],
            #     fail_silently=True,
            # )
            
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return render(request, 'core/contact.html')

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')
            
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, "Registration successful")
        return redirect('index')
        
    return render(request, 'core/register.html')

def login_view(request):
    """View for user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Get the next parameter from the request
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
            
    # Pass the next parameter to the template
    next_url = request.GET.get('next', '')
    return render(request, 'core/login.html', {'next': next_url})

@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('index')

@login_required
def profile(request, username=None):
    """User profile view"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Get user's playlists
    playlists = Playlist.objects.filter(creator=user)
    
    # Get user's recently played music
    recent_plays = PlayHistory.objects.filter(user=user).order_by('-played_at')[:10]
    
    context = {
        'user': user,
        'playlists': playlists,
        'recent_plays': recent_plays,
        'is_own_profile': user == request.user
    }
    
    return render(request, 'core/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile view"""
    user = request.user
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.bio = request.POST.get('bio', user.bio)
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
            
        user.save()
        messages.success(request, "Profile updated successfully")
        return redirect('profile')
        
    return render(request, 'core/edit_profile.html', {'user': user})

@login_required
def music_list(request):
    """View for listing music with filters"""
    # Get filter parameters
    search_query = request.GET.get('q', '')
    genre_filter = request.GET.get('genre', '')
    uploader_filter = request.GET.get('uploader', '')
    sort_by = request.GET.get('sort', 'latest')
    
    # Base query
    music_query = Music.objects.filter(is_approved=True)
    
    # Apply search filter
    if search_query:
        music_query = music_query.filter(
            Q(title__icontains=search_query) | 
            Q(artist__icontains=search_query) | 
            Q(album__icontains=search_query)
        )
    
    # Apply genre filter
    if genre_filter:
        # Try to filter by genre_fk first, then fall back to text genre
        try:
            genre = Genre.objects.get(name=genre_filter)
            music_query = music_query.filter(Q(genre_fk=genre) | Q(genre=genre_filter))
        except Genre.DoesNotExist:
            music_query = music_query.filter(genre=genre_filter)
    
    # Apply uploader filter
    if uploader_filter:
        music_query = music_query.filter(uploader_id=uploader_filter)
    
    # Apply sorting
    if sort_by == 'popular':
        music_query = music_query.order_by('-plays_count')
    elif sort_by == 'rating':
        music_query = music_query.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')
    else:  # latest
        music_query = music_query.order_by('-upload_date')
    
    # Get all genres for filter dropdown
    all_genres = Genre.objects.all().order_by('name')
    
    # Get uploaders for filter dropdown
    uploaders = User.objects.filter(uploaded_music__isnull=False).distinct()
    
    context = {
        'music_list': music_query,
        'genres': all_genres,
        'uploaders': uploaders,
        'search_query': search_query,
        'genre_filter': genre_filter,
        'uploader_filter': uploader_filter,
        'sort_by': sort_by,
    }
    
    return render(request, 'core/music_list.html', context)

@login_required
def music_detail(request, music_id):
    """View for displaying music details"""
    music = get_object_or_404(Music, id=music_id, is_approved=True)
    
    # Get user rating if logged in
    user_rating = None
    try:
        user_rating = Rating.objects.get(user=request.user, music=music)
    except Rating.DoesNotExist:
        pass
    
    # Get similar music - first try genre_fk, then fallback to text genre
    if music.genre_fk:
        similar_music = Music.objects.filter(
            Q(artist=music.artist) | Q(genre_fk=music.genre_fk),
            is_approved=True
        ).exclude(id=music.id)[:5]
    else:
        similar_music = Music.objects.filter(
            Q(artist=music.artist) | Q(genre=music.genre),
            is_approved=True
        ).exclude(id=music.id)[:5]
    
    context = {
        'music': music,
        'user_rating': user_rating,
        'similar_music': similar_music,
    }
    
    return render(request, 'core/music_detail.html', context)

@login_required
def play_music(request, music_id):
    """Handle music play event"""
    music = get_object_or_404(Music, id=music_id, is_approved=True)
    
    # Increment play count
    music.plays_count += 1
    music.save()
    
    # Record play history
    PlayHistory.objects.create(
        user=request.user,
        music=music,
        played_at=timezone.now(),
        duration_played=0  # Will be updated when play ends
    )
    
    # Record user activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='PLAY',
        target_id=music.id
    )
    
    return JsonResponse({'success': True})

@login_required
def rate_music(request, music_id):
    """Handle music rating"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
        
    music = get_object_or_404(Music, id=music_id, is_approved=True)
    rating_value = int(request.POST.get('rating', 0))
    liked = request.POST.get('liked') == 'true'
    
    if rating_value < 0 or rating_value > 5:
        return JsonResponse({'error': 'Invalid rating value'}, status=400)
    
    # Update or create rating
    rating, created = Rating.objects.update_or_create(
        user=request.user,
        music=music,
        defaults={'rating': rating_value, 'liked': liked}
    )
    
    # Record user activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='RATE',
        target_id=music.id
    )
    
    if liked:
        UserActivity.objects.create(
            user=request.user,
            activity_type='LIKE',
            target_id=music.id
        )
    
    return JsonResponse({'success': True})

@login_required
def playlist_list(request):
    """View for listing user playlists"""
    user_playlists = Playlist.objects.filter(creator=request.user)
    public_playlists = Playlist.objects.filter(is_public=True).exclude(creator=request.user)
    
    context = {
        'user_playlists': user_playlists,
        'public_playlists': public_playlists,
    }
    
    return render(request, 'core/playlist_list.html', context)

@login_required
def playlist_detail(request, playlist_id):
    """View for displaying playlist details"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    
    # Check if user has access to this playlist
    if not playlist.is_public and playlist.creator != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this playlist")
        return redirect('playlist_list')
    
    # Get playlist items
    items = PlaylistItem.objects.filter(playlist=playlist).order_by('order')
    
    context = {
        'playlist': playlist,
        'items': items,
    }
    
    return render(request, 'core/playlist_detail.html', context)

@login_required
def create_playlist(request):
    """View for creating a new playlist"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'
        
        if not name:
            messages.error(request, "Playlist name is required")
            return redirect('create_playlist')
        
        # Create playlist
        playlist = Playlist.objects.create(
            name=name,
            description=description,
            creator=request.user,
            is_public=is_public
        )
        
        if 'cover_image' in request.FILES:
            playlist.cover_image = request.FILES['cover_image']
            playlist.save()
        
        # Record user activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='CREATE_PLAYLIST',
            target_id=playlist.id
        )
        
        messages.success(request, "Playlist created successfully")
        return redirect('playlist_detail', playlist_id=playlist.id)
    
    return render(request, 'core/create_playlist.html')

@login_required
def add_to_playlist(request, music_id=None):
    """Add music to a playlist"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    # Get the music ID from the form if not in URL
    if music_id is None:
        music_id = request.POST.get('music_id')
        
    if not music_id:
        return JsonResponse({'error': 'Music ID is required'}, status=400)
    
    music = get_object_or_404(Music, id=music_id, is_approved=True)
    
    # Check if creating a new playlist
    new_playlist_name = request.POST.get('new_playlist_name')
    if new_playlist_name:
        # Create a new playlist
        is_public = request.POST.get('new_playlist_public') == 'on'
        playlist = Playlist.objects.create(
            name=new_playlist_name,
            creator=request.user,
            is_public=is_public
        )
        
        # Record user activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='CREATE_PLAYLIST',
            target_id=playlist.id
        )
    else:
        # Use existing playlist
        playlist_id = request.POST.get('playlist_id')
        if not playlist_id:
            return JsonResponse({'error': 'Playlist ID or new playlist name is required'}, status=400)
        
        playlist = get_object_or_404(Playlist, id=playlist_id)
        
        # Check if user owns the playlist
        if playlist.creator != request.user:
            return JsonResponse({'error': 'You do not own this playlist'}, status=403)
    
    # Check if music is already in playlist
    if PlaylistItem.objects.filter(playlist=playlist, music=music).exists():
        messages.info(request, f"'{music.title}' is already in '{playlist.name}'")
        return JsonResponse({
            'success': True,
            'message': f"'{music.title}' is already in '{playlist.name}'",
            'playlist_id': playlist.id
        })
    
    # Get the highest order in the playlist
    max_order = PlaylistItem.objects.filter(playlist=playlist).aggregate(max_order=Max('order'))['max_order'] or 0
    
    # Add music to playlist
    PlaylistItem.objects.create(
        playlist=playlist,
        music=music,
        order=max_order + 1
    )
    
    # Record user activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='ADD_TO_PLAYLIST',
        target_id=playlist.id
    )
    
    messages.success(request, f"Added '{music.title}' to '{playlist.name}'")
    return JsonResponse({
        'success': True,
        'message': f"Added '{music.title}' to '{playlist.name}'",
        'playlist_id': playlist.id
    })

@login_required
def remove_from_playlist(request, item_id):
    """Remove music from a playlist"""
    item = get_object_or_404(PlaylistItem, id=item_id)
    
    # Check if user owns the playlist
    if item.playlist.creator != request.user:
        messages.error(request, "You don't have permission to modify this playlist")
        return redirect('playlist_detail', playlist_id=item.playlist.id)
    
    playlist_id = item.playlist.id
    item.delete()
    
    messages.success(request, "Song removed from playlist")
    return redirect('playlist_detail', playlist_id=playlist_id)

@login_required
def edit_playlist(request, playlist_id):
    """View for editing an existing playlist"""
    playlist = get_object_or_404(Playlist, id=playlist_id)
    
    # Check if user owns the playlist
    if playlist.creator != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to edit this playlist")
        return redirect('playlist_detail', playlist_id=playlist_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'
        
        if not name:
            messages.error(request, "Playlist name is required")
            return redirect('edit_playlist', playlist_id=playlist_id)
        
        # Update playlist
        playlist.name = name
        playlist.description = description
        playlist.is_public = is_public
        
        if 'cover_image' in request.FILES:
            playlist.cover_image = request.FILES['cover_image']
        
        playlist.save()
        
        messages.success(request, "Playlist updated successfully")
        return redirect('playlist_detail', playlist_id=playlist_id)
    
    context = {
        'playlist': playlist,
    }
    
    return JsonResponse({
        'success': True,
        'playlist': {
            'id': playlist.id,
            'name': playlist.name,
            'description': playlist.description or '',
            'is_public': playlist.is_public,
            'cover_image': playlist.cover_image.url if playlist.cover_image else None
        }
    })

@login_required
def search(request):
    query = request.GET.get('q', '')
    
    # Initialize empty results
    music_results = []
    playlists_results = []
    users_results = []
    
    if query:
        # Search for music
        music_results = Music.objects.filter(
            models.Q(title__icontains=query) | 
            models.Q(artist__icontains=query) | 
            models.Q(album__icontains=query) |
            models.Q(genre__icontains=query)
        ).distinct()
        
        # Search for playlists (only public ones or user's own)
        playlists_results = Playlist.objects.filter(
            models.Q(name__icontains=query) | 
            models.Q(description__icontains=query)
        ).filter(
            models.Q(is_public=True) | models.Q(creator=request.user)
        ).distinct()
        
        # Search for users
        users_results = User.objects.filter(
            models.Q(username__icontains=query) |
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query)
        ).distinct()
    
    context = {
        'query': query,
        'music_results': music_results,
        'playlists_results': playlists_results,
        'users_results': users_results,
        'music_count': len(music_results),
        'playlists_count': len(playlists_results),
        'users_count': len(users_results),
    }
    
    return render(request, 'core/search_results.html', context)

@login_required
def get_user_playlists(request):
    """API endpoint to get user playlists for the 'Add to Playlist' modal"""
    playlists = Playlist.objects.filter(creator=request.user)
    
    # Format playlists data for JSON response
    playlists_data = []
    for playlist in playlists:
        playlist_data = {
            'id': playlist.id,
            'name': playlist.name,
            'is_public': playlist.is_public,
            'item_count': PlaylistItem.objects.filter(playlist=playlist).count(),
            'cover_image': playlist.cover_image.url if playlist.cover_image else None
        }
        playlists_data.append(playlist_data)
    
    return JsonResponse({
        'success': True,
        'playlists': playlists_data
    })

@login_required
def manage_genres(request):
    """View for admins to manage genres"""
    # Only staff members can manage genres
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page")
        return redirect('index')
    
    genres = Genre.objects.all().order_by('name')
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'add':
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            
            if not name:
                messages.error(request, "Genre name is required")
            elif Genre.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Genre '{name}' already exists")
            else:
                genre = Genre.objects.create(name=name, description=description)
                
                # Handle image upload
                if 'image' in request.FILES:
                    genre.image = request.FILES['image']
                    genre.save()
                    
                messages.success(request, f"Genre '{name}' added successfully")
                return redirect('manage_genres')
        
        elif action == 'delete':
            genre_id = request.POST.get('genre_id')
            if genre_id:
                try:
                    genre = Genre.objects.get(id=genre_id)
                    name = genre.name
                    genre.delete()
                    messages.success(request, f"Genre '{name}' deleted successfully")
                    return redirect('manage_genres')
                except Genre.DoesNotExist:
                    messages.error(request, "Genre not found")
        
        elif action == 'edit':
            genre_id = request.POST.get('genre_id')
            new_name = request.POST.get('name', '').strip()
            new_description = request.POST.get('description', '').strip()
            
            if not genre_id or not new_name:
                messages.error(request, "Genre ID and name are required")
            else:
                try:
                    genre = Genre.objects.get(id=genre_id)
                    if Genre.objects.filter(name__iexact=new_name).exclude(id=genre_id).exists():
                        messages.error(request, f"Genre '{new_name}' already exists")
                    else:
                        genre.name = new_name
                        genre.description = new_description
                        
                        # Handle image upload
                        if 'image' in request.FILES:
                            genre.image = request.FILES['image']
                            
                        genre.save()
                        messages.success(request, f"Genre '{new_name}' updated successfully")
                        return redirect('manage_genres')
                except Genre.DoesNotExist:
                    messages.error(request, "Genre not found")
    
    context = {
        'genres': genres,
    }
    
    return render(request, 'core/manage_genres.html', context)

@login_required
def genre_detail(request, genre_id):
    """View for displaying genre details and all music in that genre"""
    genre = get_object_or_404(Genre, id=genre_id)
    
    # Get all music in this genre
    music_list = Music.objects.filter(
        Q(genre_fk=genre) | Q(genre=genre.name),
        is_approved=True
    ).order_by('-upload_date')
    
    # Get related genres (for sidebar)
    related_genres = Genre.objects.exclude(id=genre_id).order_by('?')[:5]
    
    context = {
        'genre': genre,
        'music_list': music_list,
        'related_genres': related_genres,
    }
    
    return render(request, 'core/genre_detail.html', context)
