from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('music/', views.music_list, name='music_list'),
    path('music/<int:music_id>/', views.music_detail, name='music_detail'),
    path('music/<int:music_id>/play/', views.play_music, name='play_music'),
    path('music/<int:music_id>/rate/', views.rate_music, name='rate_music'),
    path('playlists/', views.playlist_list, name='playlist_list'),
    path('playlists/<int:playlist_id>/', views.playlist_detail, name='playlist_detail'),
    path('playlists/create/', views.create_playlist, name='create_playlist'),
    path('playlists/<int:playlist_id>/edit/', views.edit_playlist, name='edit_playlist'),
    path('music/<int:music_id>/add-to-playlist/', views.add_to_playlist, name='add_to_playlist_with_id'),
    path('add-to-playlist/', views.add_to_playlist, name='add_to_playlist'),
    path('playlists/item/<int:item_id>/remove/', views.remove_from_playlist, name='remove_from_playlist'),
    path('search/', views.search, name='search'),
    path('api/playlists/', views.get_user_playlists, name='get_user_playlists'),
    path('admin/core/genre/', views.manage_genres, name='manage_genres'),
    path('genres/<int:genre_id>/', views.genre_detail, name='genre_detail'),
] 