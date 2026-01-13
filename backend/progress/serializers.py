"""
Serializers for progress tracking.
"""
from rest_framework import serializers
from .models import CourseProgress, VideoProgress, Certificate


class VideoProgressSerializer(serializers.ModelSerializer):
    """Serializer for video progress."""
    
    video_title = serializers.CharField(source='video.title', read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = VideoProgress
        fields = [
            'id', 'video', 'video_title', 'watched_seconds', 'total_seconds',
            'is_completed', 'completed_at', 'last_position_seconds',
            'watch_count', 'progress_percentage', 'last_watched_at'
        ]
        read_only_fields = ['first_watched_at', 'last_watched_at']


class UpdateVideoProgressSerializer(serializers.Serializer):
    """Serializer for updating video progress."""
    
    video_id = serializers.IntegerField()
    watched_seconds = serializers.IntegerField(min_value=0)
    total_seconds = serializers.IntegerField(min_value=0)
    last_position_seconds = serializers.IntegerField(min_value=0, required=False, default=0)
    is_completed = serializers.BooleanField(required=False, default=False)


class CourseProgressSerializer(serializers.ModelSerializer):
    """Serializer for course progress."""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = CourseProgress
        fields = [
            'id', 'course', 'course_title', 'course_slug',
            'videos_completed', 'total_videos',
            'quizzes_completed', 'quizzes_passed', 'total_quizzes',
            'progress_percentage', 'is_completed',
            'last_accessed_at', 'started_at', 'completed_at'
        ]


class CourseProgressDetailSerializer(serializers.ModelSerializer):
    """Detailed course progress with video progress."""
    
    course_title = serializers.CharField(source='course.title', read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    video_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseProgress
        fields = [
            'id', 'course', 'course_title',
            'videos_completed', 'total_videos',
            'quizzes_completed', 'quizzes_passed', 'total_quizzes',
            'progress_percentage', 'is_completed',
            'last_accessed_at', 'started_at', 'completed_at',
            'video_progress'
        ]
    
    def get_video_progress(self, obj):
        videos = obj.course.modules.values_list('videos', flat=True)
        progress = VideoProgress.objects.filter(
            user=obj.user,
            video__in=videos
        )
        return VideoProgressSerializer(progress, many=True).data


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for certificates."""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'course', 'course_title',
            'certificate_number', 'issued_at',
            'verification_url', 'pdf_url'
        ]
        read_only_fields = ['certificate_number', 'issued_at']


class StudentProgressReportSerializer(serializers.Serializer):
    """Serializer for student progress reports (admin view)."""
    
    user_id = serializers.IntegerField()
    user_email = serializers.EmailField()
    user_name = serializers.CharField()
    courses_enrolled = serializers.IntegerField()
    courses_completed = serializers.IntegerField()
    overall_progress = serializers.FloatField()
    quizzes_taken = serializers.IntegerField()
    average_quiz_score = serializers.FloatField()
    certificates_earned = serializers.IntegerField()
