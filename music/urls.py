from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='music/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='music/logout.html'), name='logout'),
    path('song/<int:song_id>/', views.song_detail, name='song-detail'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('social-auth/', include('social_django.urls', namespace='social')),
] 