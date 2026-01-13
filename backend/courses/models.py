"""
Models for courses and course content.
"""
from django.db import models
from django.conf import settings


class Category(models.Model):
    """Category for organizing courses."""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name (e.g., 'fa-code')")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """Course model containing videos and resources."""
    
    class Level(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'
    
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    thumbnail = models.URLField(max_length=500, blank=True, null=True)
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses_created'
    )
    
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    duration_hours = models.PositiveIntegerField(default=0, help_text="Estimated duration in hours")
    is_featured = models.BooleanField(default=False)
    
    prerequisites = models.TextField(blank=True, help_text="Prerequisites for this course")
    learning_objectives = models.TextField(blank=True, help_text="What students will learn")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'course'
        verbose_name_plural = 'courses'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def total_videos(self):
        """Get total number of videos in the course."""
        return self.modules.aggregate(
            total=models.Count('videos')
        )['total'] or 0
    
    @property
    def total_duration_minutes(self):
        """Get total duration of all videos in minutes."""
        return self.modules.aggregate(
            total=models.Sum('videos__duration_minutes')
        )['total'] or 0
    
    @property
    def enrolled_students_count(self):
        """Get the number of enrolled students."""
        return self.enrollments.count()


class Module(models.Model):
    """Module/Section within a course."""
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'module'
        verbose_name_plural = 'modules'
        ordering = ['order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def total_duration_minutes(self):
        """Get total duration of videos in this module."""
        return self.videos.aggregate(
            total=models.Sum('duration_minutes')
        )['total'] or 0


class Video(models.Model):
    """Video lesson within a module."""
    
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Google Drive video information
    google_drive_file_id = models.CharField(max_length=100)
    google_drive_url = models.URLField(max_length=500)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    
    is_preview = models.BooleanField(default=False, help_text="Allow preview without enrollment")
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'video'
        verbose_name_plural = 'videos'
        ordering = ['order']
        unique_together = ['module', 'order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"


class Resource(models.Model):
    """Downloadable resource attached to a course or module."""
    
    class ResourceType(models.TextChoices):
        PDF = 'pdf', 'PDF Document'
        DOC = 'doc', 'Word Document'
        SPREADSHEET = 'spreadsheet', 'Spreadsheet'
        PRESENTATION = 'presentation', 'Presentation'
        CODE = 'code', 'Code File'
        OTHER = 'other', 'Other'
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='resources',
        null=True,
        blank=True
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='resources',
        null=True,
        blank=True
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.OTHER
    )
    
    # Google Drive resource information
    google_drive_file_id = models.CharField(max_length=100)
    google_drive_url = models.URLField(max_length=500)
    file_size_bytes = models.BigIntegerField(default=0)
    
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'resource'
        verbose_name_plural = 'resources'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """Student enrollment in a course."""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        DROPPED = 'dropped', 'Dropped'
        EXPIRED = 'expired', 'Expired'
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Assigned by admin
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollments_assigned'
    )
    
    class Meta:
        verbose_name = 'enrollment'
        verbose_name_plural = 'enrollments'
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
