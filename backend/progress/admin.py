"""
Admin configuration for progress tracking.
"""
from django.contrib import admin
from .models import CourseProgress, VideoProgress, Certificate


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'videos_completed', 'total_videos', 'progress_percentage', 'completed_at')
    list_filter = ('course', 'completed_at')
    search_fields = ('user__email', 'course__title')
    raw_id_fields = ('user', 'course')
    
    def progress_percentage(self, obj):
        return f"{obj.progress_percentage}%"


@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'is_completed', 'progress_percentage', 'watch_count', 'last_watched_at')
    list_filter = ('is_completed', 'video__module__course')
    search_fields = ('user__email', 'video__title')
    raw_id_fields = ('user', 'video')
    
    def progress_percentage(self, obj):
        return f"{obj.progress_percentage}%"


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'user', 'course', 'issued_at')
    list_filter = ('course', 'issued_at')
    search_fields = ('certificate_number', 'user__email', 'course__title')
    raw_id_fields = ('user', 'course')
    readonly_fields = ('certificate_number', 'issued_at')
