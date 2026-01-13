"""
Views for progress tracking.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Count, Q
from django.contrib.auth import get_user_model

from .models import CourseProgress, VideoProgress, Certificate
from .serializers import (
    CourseProgressSerializer, CourseProgressDetailSerializer,
    VideoProgressSerializer, UpdateVideoProgressSerializer,
    CertificateSerializer, StudentProgressReportSerializer
)
from courses.models import Course, Video, Enrollment
from quizzes.models import QuizAttempt
from accounts.permissions import IsAdmin

User = get_user_model()


class MyCourseProgressListView(generics.ListAPIView):
    """List current user's course progress."""
    
    serializer_class = CourseProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CourseProgress.objects.filter(
            user=self.request.user
        ).select_related('course')


class CourseProgressDetailView(generics.RetrieveAPIView):
    """Get detailed progress for a specific course."""
    
    serializer_class = CourseProgressDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        course_slug = self.kwargs.get('course_slug')
        progress, created = CourseProgress.objects.get_or_create(
            user=self.request.user,
            course__slug=course_slug,
            defaults={'course': Course.objects.get(slug=course_slug)}
        )
        if created:
            progress.update_totals()
        return progress


class UpdateVideoProgressView(APIView):
    """Update video progress."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = UpdateVideoProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            video = Video.objects.get(id=serializer.validated_data['video_id'])
        except Video.DoesNotExist:
            return Response(
                {'error': 'Video not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create video progress
        progress, created = VideoProgress.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={
                'total_seconds': video.duration_minutes * 60
            }
        )
        
        # Update progress
        progress.watched_seconds = max(
            progress.watched_seconds,
            serializer.validated_data['watched_seconds']
        )
        progress.total_seconds = serializer.validated_data['total_seconds']
        progress.last_position_seconds = serializer.validated_data.get(
            'last_position_seconds', 0
        )
        progress.watch_count += 1 if created else 0
        
        # Mark as completed if watched enough (90%)
        if serializer.validated_data.get('is_completed') or progress.progress_percentage >= 90:
            if not progress.is_completed:
                progress.is_completed = True
                progress.completed_at = timezone.now()
                
                # Update course progress
                self._update_course_progress(request.user, video)
        
        progress.save()
        
        return Response(VideoProgressSerializer(progress).data)
    
    def _update_course_progress(self, user, video):
        """Update course progress when a video is completed."""
        course = video.module.course
        
        course_progress, created = CourseProgress.objects.get_or_create(
            user=user,
            course=course
        )
        
        # Count completed videos
        completed_videos = VideoProgress.objects.filter(
            user=user,
            video__module__course=course,
            is_completed=True
        ).count()
        
        course_progress.videos_completed = completed_videos
        course_progress.update_totals()
        
        # Check if course is completed
        if course_progress.videos_completed >= course_progress.total_videos:
            # Check required quizzes
            from quizzes.models import Quiz
            required_quizzes = Quiz.objects.filter(
                Q(course=course) | Q(module__course=course) | Q(video__module__course=course),
                is_required=True
            )
            
            passed_quizzes = QuizAttempt.objects.filter(
                user=user,
                quiz__in=required_quizzes,
                passed=True
            ).values('quiz').distinct().count()
            
            course_progress.quizzes_passed = passed_quizzes
            
            if passed_quizzes >= required_quizzes.count():
                course_progress.completed_at = timezone.now()
                
                # Update enrollment status
                enrollment = Enrollment.objects.filter(
                    user=user, course=course
                ).first()
                if enrollment:
                    enrollment.status = Enrollment.Status.COMPLETED
                    enrollment.completed_at = timezone.now()
                    enrollment.save()
        
        course_progress.save()


class VideoProgressListView(generics.ListAPIView):
    """List video progress for a course."""
    
    serializer_class = VideoProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        return VideoProgress.objects.filter(
            user=self.request.user,
            video__module__course__slug=course_slug
        ).select_related('video')


class MyCertificatesView(generics.ListAPIView):
    """List current user's certificates."""
    
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Certificate.objects.filter(
            user=self.request.user
        ).select_related('course')


class CertificateDetailView(generics.RetrieveAPIView):
    """Verify a certificate by number."""
    
    serializer_class = CertificateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'certificate_number'
    queryset = Certificate.objects.all()


class IssueCertificateView(APIView):
    """Issue certificate for completed course."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, course_slug):
        try:
            course = Course.objects.get(slug=course_slug)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if course is completed
        try:
            progress = CourseProgress.objects.get(
                user=request.user,
                course=course
            )
        except CourseProgress.DoesNotExist:
            return Response(
                {'error': 'No progress found for this course.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not progress.is_completed:
            return Response(
                {'error': 'Course not yet completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if certificate already exists
        certificate, created = Certificate.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        if not created:
            return Response(
                {'message': 'Certificate already issued.', 'certificate': CertificateSerializer(certificate).data}
            )
        
        return Response(
            CertificateSerializer(certificate).data,
            status=status.HTTP_201_CREATED
        )


# Admin Views
class StudentProgressReportView(APIView):
    """Get progress report for all students (admin only)."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get(self, request):
        students = User.objects.filter(role=User.Role.STUDENT)
        reports = []
        
        for student in students:
            enrollments = Enrollment.objects.filter(user=student)
            completed = enrollments.filter(status=Enrollment.Status.COMPLETED).count()
            
            quiz_attempts = QuizAttempt.objects.filter(
                user=student,
                status=QuizAttempt.Status.COMPLETED
            )
            
            avg_score = quiz_attempts.aggregate(avg=Avg('score'))['avg'] or 0
            
            course_progress = CourseProgress.objects.filter(user=student)
            overall = course_progress.aggregate(avg=Avg('videos_completed'))['avg'] or 0
            
            reports.append({
                'user_id': student.id,
                'user_email': student.email,
                'user_name': student.full_name,
                'courses_enrolled': enrollments.count(),
                'courses_completed': completed,
                'overall_progress': overall,
                'quizzes_taken': quiz_attempts.count(),
                'average_quiz_score': round(avg_score, 2),
                'certificates_earned': Certificate.objects.filter(user=student).count()
            })
        
        return Response(reports)


class CourseProgressReportView(APIView):
    """Get progress report for a specific course (admin only)."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get(self, request, course_slug):
        try:
            course = Course.objects.get(slug=course_slug)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        progress_records = CourseProgress.objects.filter(
            course=course
        ).select_related('user')
        
        data = {
            'course_id': course.id,
            'course_title': course.title,
            'total_enrolled': course.enrollments.count(),
            'total_completed': progress_records.filter(completed_at__isnull=False).count(),
            'average_progress': progress_records.aggregate(
                avg=Avg('videos_completed')
            )['avg'] or 0,
            'students': CourseProgressSerializer(progress_records, many=True).data
        }
        
        return Response(data)
