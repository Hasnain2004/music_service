from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Song, Rating, UserSession, ContactMessage
from .forms import UserRegisterForm, RatingForm, UserProfileForm
from django.utils import timezone

def home(request):
    songs = Song.objects.filter(is_active=True)
    search_query = request.GET.get('search', '')
    genre_filter = request.GET.get('genre', '')
    
    if search_query:
        songs = songs.filter(title__icontains=search_query) | songs.filter(artist__icontains=search_query)
    
    if genre_filter:
        songs = songs.filter(genre=genre_filter)
    
    # Get unique genres for the filter dropdown
    genres = Song.objects.values_list('genre', flat=True).distinct()
    
    # Add average rating to each song
    songs = songs.annotate(avg_rating=Avg('rating__rating'))
    
    context = {
        'songs': songs,
        'genres': genres,
    }
    return render(request, 'music/home.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    # Store the next URL in session if provided
    next_url = request.GET.get('next')
    if next_url:
        request.session['next'] = next_url
    
    return render(request, 'music/login.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'music/register.html', {'form': form})

@login_required
def song_detail(request, song_id):
    song = get_object_or_404(Song, id=song_id, is_active=True)
    
    # Track user session only for logged-in users
    if request.user.is_authenticated:
        UserSession.objects.create(user=request.user, song=song)
    
    # Get average rating
    avg_rating = Rating.objects.filter(song=song).aggregate(Avg('rating'))['rating__avg']
    
    # Only show rating form to logged-in users
    form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = RatingForm(request.POST)
            if form.is_valid():
                # Try to get existing rating
                rating, created = Rating.objects.get_or_create(
                    user=request.user,
                    song=song,
                    defaults={'rating': form.cleaned_data['rating']}
                )
                
                # If rating already exists, update it
                if not created:
                    rating.rating = form.cleaned_data['rating']
                    rating.save()
                
                messages.success(request, 'Rating submitted successfully!')
                return redirect('song-detail', song_id=song.id)
        else:
            # Pre-fill form with existing rating if any
            try:
                existing_rating = Rating.objects.get(user=request.user, song=song)
                form = RatingForm(initial={'rating': existing_rating.rating})
            except Rating.DoesNotExist:
                form = RatingForm()
    
    context = {
        'song': song,
        'form': form,
        'avg_rating': avg_rating,
    }
    return render(request, 'music/song_detail.html', context)

@login_required
def profile(request):
    # Get user sessions and ratings
    user_sessions = UserSession.objects.filter(user=request.user).order_by('-last_played')
    user_ratings = Rating.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'user_sessions': user_sessions,
        'user_ratings': user_ratings,
        'form': form
    }
    return render(request, 'music/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'music/edit_profile.html', {'form': form})

def about(request):
    return render(request, 'music/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        ContactMessage.objects.create(name=name, email=email, message=message)
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
    return render(request, 'music/contact.html')
