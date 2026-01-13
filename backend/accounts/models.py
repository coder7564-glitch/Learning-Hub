"""
User models for LMS.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager for the User model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as the primary identifier."""
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        STUDENT = 'student', 'Student'
    
    username = None
    email = models.EmailField('email address', unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )
    profile_picture = models.URLField(max_length=500, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Google OAuth tokens for Drive access
    google_access_token = models.TextField(blank=True, null=True)
    google_refresh_token = models.TextField(blank=True, null=True)
    google_token_expiry = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == self.Role.ADMIN or self.is_superuser
    
    @property
    def is_student(self):
        """Check if user is a student."""
        return self.role == self.Role.STUDENT


class StudentProfile(models.Model):
    """Extended profile for students."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    enrollment_date = models.DateField(auto_now_add=True)
    graduation_date = models.DateField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'student profile'
        verbose_name_plural = 'student profiles'
    
    def __str__(self):
        return f"Student Profile: {self.user.email}"


class AdminProfile(models.Model):
    """Extended profile for admins."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_profile'
    )
    department = models.CharField(max_length=100, blank=True)
    can_manage_users = models.BooleanField(default=True)
    can_manage_courses = models.BooleanField(default=True)
    can_view_reports = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'admin profile'
        verbose_name_plural = 'admin profiles'
    
    def __str__(self):
        return f"Admin Profile: {self.user.email}"
