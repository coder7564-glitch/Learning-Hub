"""
Views for courses.
"""
from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Category, Course, Module, Video, Resource, Enrollment
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    CourseCreateSerializer, ModuleSerializer, ModuleCreateSerializer,
    VideoSerializer, VideoCreateSerializer, ResourceSerializer,
    ResourceCreateSerializer, EnrollmentSerializer, EnrollmentCreateSerializer,
    BulkEnrollmentSerializer
)
from accounts.permissions import IsAdmin, IsAdminOrReadOnly, IsEnrolledOrAdmin

User = get_user_model()


# Category Views
class CategoryListView(generics.ListCreateAPIView):
    """List and create categories."""
    
    queryset = Category.objects.filter(is_active=True, parent__isnull=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name', 'description']


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete category."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


# Course Views
class CourseListView(generics.ListCreateAPIView):
    """List and create courses."""
    
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['category', 'level', 'status', 'is_featured']
    search_fields = ['title', 'description', 'short_description']
    ordering_fields = ['created_at', 'title', 'enrolled_students_count']
    
    def get_queryset(self):
        queryset = Course.objects.select_related('category', 'instructor')
        user = self.request.user
        
        # Non-admin users only see published courses
        if not user.is_authenticated or not user.is_admin:
            queryset = queryset.filter(status=Course.Status.PUBLISHED)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateSerializer
        return CourseListSerializer


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete course."""
    
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Course.objects.select_related('category', 'instructor').prefetch_related('modules__videos', 'resources')
        user = self.request.user
        
        if not user.is_authenticated or not user.is_admin:
            queryset = queryset.filter(status=Course.Status.PUBLISHED)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CourseCreateSerializer
        return CourseDetailSerializer


class FeaturedCoursesView(generics.ListAPIView):
    """List featured courses."""
    
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Course.objects.filter(
            status=Course.Status.PUBLISHED,
            is_featured=True
        ).select_related('category', 'instructor')[:6]


# Module Views
class ModuleListCreateView(generics.ListCreateAPIView):
    """List and create modules for a course."""
    
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        return Module.objects.filter(course__slug=course_slug).prefetch_related('videos', 'resources')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ModuleCreateSerializer
        return ModuleSerializer


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete module."""
    
    queryset = Module.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ModuleCreateSerializer
        return ModuleSerializer


# Video Views
class VideoListCreateView(generics.ListCreateAPIView):
    """List and create videos."""
    
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        module_id = self.kwargs.get('module_id')
        if module_id:
            return Video.objects.filter(module_id=module_id)
        return Video.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VideoCreateSerializer
        return VideoSerializer


class VideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete video."""
    
    queryset = Video.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return VideoCreateSerializer
        return VideoSerializer


# Resource Views
class ResourceListCreateView(generics.ListCreateAPIView):
    """List and create resources."""
    
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        if course_slug:
            return Resource.objects.filter(
                Q(course__slug=course_slug) | Q(module__course__slug=course_slug)
            )
        return Resource.objects.all()
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResourceCreateSerializer
        return ResourceSerializer


class ResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete resource."""
    
    queryset = Resource.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ResourceCreateSerializer
        return ResourceSerializer


# Enrollment Views
class EnrollmentListView(generics.ListAPIView):
    """List enrollments (admin sees all, students see their own)."""
    
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'course']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Enrollment.objects.select_related('user', 'course').all()
        return Enrollment.objects.filter(user=user).select_related('course')


class EnrollmentCreateView(generics.CreateAPIView):
    """Create enrollment (admin assigns, students self-enroll)."""
    
    serializer_class = EnrollmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin:
            serializer.save(assigned_by=user)
        else:
            serializer.save(user=user)


class SelfEnrollView(APIView):
    """Allow students to enroll themselves in a course."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, course_slug):
        try:
            course = Course.objects.get(slug=course_slug, status=Course.Status.PUBLISHED)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'status': Enrollment.Status.ACTIVE}
        )
        
        if not created:
            return Response(
                {'message': 'Already enrolled in this course.'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )


class BulkEnrollView(APIView):
    """Bulk enroll students in a course (admin only)."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def post(self, request):
        serializer = BulkEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        course = Course.objects.get(id=serializer.validated_data['course_id'])
        user_ids = serializer.validated_data['user_ids']
        expires_at = serializer.validated_data.get('expires_at')
        
        created_enrollments = []
        existing_enrollments = []
        
        for user_id in user_ids:
            try:
                user = User.objects.get(id=user_id)
                enrollment, created = Enrollment.objects.get_or_create(
                    user=user,
                    course=course,
                    defaults={
                        'status': Enrollment.Status.ACTIVE,
                        'assigned_by': request.user,
                        'expires_at': expires_at
                    }
                )
                if created:
                    created_enrollments.append(enrollment)
                else:
                    existing_enrollments.append(enrollment)
            except User.DoesNotExist:
                continue
        
        return Response({
            'created': len(created_enrollments),
            'existing': len(existing_enrollments),
            'enrollments': EnrollmentSerializer(created_enrollments, many=True).data
        })


class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage individual enrollment."""
    
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = Enrollment.objects.all()


class MarkCourseCompleteView(APIView):
    """Mark a course as complete for a student (admin only)."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def post(self, request, enrollment_id):
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id)
        except Enrollment.DoesNotExist:
            return Response(
                {'error': 'Enrollment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        enrollment.status = Enrollment.Status.COMPLETED
        enrollment.completed_at = timezone.now()
        enrollment.save()
        
        return Response(EnrollmentSerializer(enrollment).data)


# Student Course Views
class MyCoursesView(generics.ListAPIView):
    """List courses the current user is enrolled in."""
    
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user
        ).select_related('course', 'course__category', 'course__instructor')
