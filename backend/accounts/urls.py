"""
URL patterns for accounts.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView, UserProfileView, ChangePasswordView,
    GoogleAuthView, LogoutView, StudentListView, StudentDetailView,
    UserDetailView
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('google/', GoogleAuthView.as_view(), name='google_auth'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Admin - User Management
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
]
