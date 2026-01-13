"""
Views for user accounts.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings

from .models import StudentProfile, AdminProfile
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ChangePasswordSerializer, GoogleAuthSerializer, StudentListSerializer
)
from .permissions import IsAdmin, IsAdminOrSelf

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """View for user registration."""
    
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class ChangePasswordView(APIView):
    """View for changing password."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Incorrect password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully.'})


class GoogleAuthView(APIView):
    """View for Google OAuth2 authentication."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        access_token = serializer.validated_data['access_token']
        
        try:
            # Verify the Google token
            idinfo = id_token.verify_oauth2_token(
                access_token,
                google_requests.Request(),
                settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
            )
            
            email = idinfo.get('email')
            if not email:
                return Response(
                    {'error': 'Email not provided by Google.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': idinfo.get('given_name', ''),
                    'last_name': idinfo.get('family_name', ''),
                    'profile_picture': idinfo.get('picture', ''),
                    'is_active': True,
                }
            )
            
            if created:
                # Create student profile for new users
                StudentProfile.objects.create(user=user)
            else:
                # Update profile picture if changed
                if idinfo.get('picture'):
                    user.profile_picture = idinfo['picture']
                    user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
            
        except ValueError as e:
            return Response(
                {'error': f'Invalid token: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """View for logging out (blacklisting refresh token)."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response(
                {'error': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


# Admin Views
class StudentListView(generics.ListAPIView):
    """View for listing all students (admin only)."""
    
    serializer_class = StudentListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filterset_fields = ['is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email', 'first_name']
    
    def get_queryset(self):
        return User.objects.filter(role=User.Role.STUDENT).select_related('student_profile')


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for managing individual students (admin only)."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        return User.objects.filter(role=User.Role.STUDENT)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating any user (admin or self)."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
