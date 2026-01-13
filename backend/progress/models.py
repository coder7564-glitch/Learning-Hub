"""
Models for tracking student progress.
"""
from django.db import models
from django.conf import settings
from courses.models import Course, Module, Video


class CourseProgress(models.Model):
    """Track overall course progress for a student."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_progress'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )
    
    videos_completed = models.PositiveIntegerField(default=0)
    total_videos = models.PositiveIntegerField(default=0)
    quizzes_completed = models.PositiveIntegerField(default=0)
    quizzes_passed = models.PositiveIntegerField(default=0)
    total_quizzes = models.PositiveIntegerField(default=0)
    
    last_accessed_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'course progress'
        verbose_name_plural = 'course progress records'
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title} - {self.progress_percentage}%"
    
    @property
    def progress_percentage(self):
        """Calculate overall progress percentage."""
        if self.total_videos == 0:
            return 0
        return round((self.videos_completed / self.total_videos) * 100, 2)
    
    @property
    def is_completed(self):
        """Check if course is completed."""
        return self.videos_completed >= self.total_videos and self.completed_at is not None
    
    def update_totals(self):
        """Update total counts from course."""
        self.total_videos = self.course.total_videos
        from quizzes.models import Quiz
        self.total_quizzes = Quiz.objects.filter(
            models.Q(course=self.course) | 
            models.Q(module__course=self.course) |
            models.Q(video__module__course=self.course),
            is_required=True
        ).count()
        self.save()


class VideoProgress(models.Model):
    """Track individual video progress for a student."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='video_progress'
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )
    
    watched_seconds = models.PositiveIntegerField(default=0)
    total_seconds = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    last_position_seconds = models.PositiveIntegerField(default=0)
    watch_count = models.PositiveIntegerField(default=0)
    
    first_watched_at = models.DateTimeField(auto_now_add=True)
    last_watched_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'video progress'
        verbose_name_plural = 'video progress records'
        unique_together = ['user', 'video']
    
    def __str__(self):
        status = "Completed" if self.is_completed else f"{self.progress_percentage}%"
        return f"{self.user.email} - {self.video.title} - {status}"
    
    @property
    def progress_percentage(self):
        """Calculate video watch progress."""
        if self.total_seconds == 0:
            return 0
        return min(round((self.watched_seconds / self.total_seconds) * 100, 2), 100)


class Certificate(models.Model):
    """Certificate awarded upon course completion."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    
    # Optional fields for verification
    verification_url = models.URLField(max_length=500, blank=True)
    pdf_url = models.URLField(max_length=500, blank=True)
    
    class Meta:
        verbose_name = 'certificate'
        verbose_name_plural = 'certificates'
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"Certificate: {self.user.email} - {self.course.title}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            import uuid
            self.certificate_number = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
