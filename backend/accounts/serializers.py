"""
Serializers for user accounts.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StudentProfile, AdminProfile

User = get_user_model()


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for student profiles."""
    
    class Meta:
        model = StudentProfile
        fields = ['student_id', 'enrollment_date', 'graduation_date', 'department']
        read_only_fields = ['enrollment_date']


class AdminProfileSerializer(serializers.ModelSerializer):
    """Serializer for admin profiles."""
    
    class Meta:
        model = AdminProfile
        fields = ['department', 'can_manage_users', 'can_manage_courses', 'can_view_reports']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user objects."""
    
    full_name = serializers.ReadOnlyField()
    student_profile = StudentProfileSerializer(read_only=True)
    admin_profile = AdminProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'profile_picture', 'bio', 'phone_number',
            'is_active', 'created_at', 'updated_at',
            'student_profile', 'admin_profile'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role'
        ]
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        """Create a new user with encrypted password."""
        user = User.objects.create_user(**validated_data)
        
        # Create appropriate profile
        if user.role == User.Role.STUDENT:
            StudentProfile.objects.create(user=user)
        elif user.role == User.Role.ADMIN:
            AdminProfile.objects.create(user=user)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'phone_number', 'profile_picture']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        return attrs


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google OAuth authentication."""
    
    access_token = serializers.CharField(required=True)
    
    def validate_access_token(self, value):
        """Validate the Google access token."""
        if not value:
            raise serializers.ValidationError('Access token is required.')
        return value


class StudentListSerializer(serializers.ModelSerializer):
    """Serializer for listing students (admin view)."""
    
    full_name = serializers.ReadOnlyField()
    student_profile = StudentProfileSerializer(read_only=True)
    courses_enrolled = serializers.SerializerMethodField()
    overall_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'profile_picture', 'is_active', 'created_at',
            'student_profile', 'courses_enrolled', 'overall_progress'
        ]
    
    def get_courses_enrolled(self, obj):
        """Get the number of courses the student is enrolled in."""
        return obj.enrollments.count() if hasattr(obj, 'enrollments') else 0
    
    def get_overall_progress(self, obj):
        """Calculate overall progress across all courses."""
        from progress.models import CourseProgress
        progress_records = CourseProgress.objects.filter(user=obj)
        if not progress_records.exists():
            return 0
        total_progress = sum(p.progress_percentage for p in progress_records)
        return round(total_progress / progress_records.count(), 2)
