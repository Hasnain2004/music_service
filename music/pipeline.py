from .models import UserProfile

def create_user_profile(backend, user, response, *args, **kwargs):
    """
    Create a UserProfile for users who sign in with Google OAuth2
    """
    if backend.name == 'google-oauth2':
        # Get user data from Google
        email = response.get('email', '')
        first_name = response.get('given_name', '')
        last_name = response.get('family_name', '')
        
        # Create or update user profile
        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        ) 