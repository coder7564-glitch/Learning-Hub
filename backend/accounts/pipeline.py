"""
Social auth pipeline functions for Google OAuth.
"""
from .models import StudentProfile


def save_profile_picture(backend, user, response, *args, **kwargs):
    """Save the user's profile picture from Google."""
    if backend.name == 'google-oauth2':
        picture = response.get('picture')
        if picture and (not user.profile_picture or user.profile_picture != picture):
            user.profile_picture = picture
            user.save()


def save_google_tokens(backend, user, response, *args, **kwargs):
    """Save Google OAuth tokens for Drive API access."""
    if backend.name == 'google-oauth2':
        from datetime import datetime, timedelta
        
        access_token = response.get('access_token')
        refresh_token = response.get('refresh_token')
        expires_in = response.get('expires_in')
        
        if access_token:
            user.google_access_token = access_token
        
        if refresh_token:
            user.google_refresh_token = refresh_token
        
        if expires_in:
            user.google_token_expiry = datetime.now() + timedelta(seconds=expires_in)
        
        user.save()
        
        # Ensure student profile exists for new users
        if user.is_student and not hasattr(user, 'student_profile'):
            StudentProfile.objects.get_or_create(user=user)
