"""
Serializers for courses.
"""
from rest_framework import serializers
from .models import Category, Course, Module, Video, Resource, Enrollment


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""
    
    subcategories = serializers.SerializerMethodField()
    course_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'parent', 'order', 'is_active', 'subcategories', 'course_count'
        ]
    
    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.filter(is_active=True), many=True).data
    
    def get_course_count(self, obj):
        return obj.courses.filter(status=Course.Status.PUBLISHED).count()


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for videos."""
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'google_drive_file_id',
            'google_drive_url', 'thumbnail_url', 'duration_minutes',
            'order', 'is_preview', 'is_published', 'created_at'
        ]


class VideoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating videos."""
    
    class Meta:
        model = Video
        fields = [
            'module', 'title', 'description', 'google_drive_file_id',
            'google_drive_url', 'thumbnail_url', 'duration_minutes',
            'order', 'is_preview', 'is_published'
        ]


class ResourceSerializer(serializers.ModelSerializer):
    """Serializer for resources."""
    
    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'description', 'resource_type',
            'google_drive_file_id', 'google_drive_url',
            'file_size_bytes', 'order', 'is_published', 'created_at'
        ]


class ResourceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating resources."""
    
    class Meta:
        model = Resource
        fields = [
            'course', 'module', 'title', 'description', 'resource_type',
            'google_drive_file_id', 'google_drive_url',
            'file_size_bytes', 'order', 'is_published'
        ]


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for modules with nested videos and resources."""
    
    videos = VideoSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    total_duration_minutes = serializers.ReadOnlyField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order', 'is_published',
            'videos', 'resources', 'total_duration_minutes', 'created_at'
        ]


class ModuleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating modules."""
    
    class Meta:
        model = Module
        fields = ['course', 'title', 'description', 'order', 'is_published']


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for listing courses."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    total_videos = serializers.ReadOnlyField()
    total_duration_minutes = serializers.ReadOnlyField()
    enrolled_students_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'short_description', 'thumbnail',
            'category', 'category_name', 'instructor', 'instructor_name',
            'level', 'status', 'duration_hours', 'is_featured',
            'total_videos', 'total_duration_minutes', 'enrolled_students_count',
            'created_at', 'published_at'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for course details with modules."""
    
    category = CategorySerializer(read_only=True)
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    total_videos = serializers.ReadOnlyField()
    total_duration_minutes = serializers.ReadOnlyField()
    enrolled_students_count = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'thumbnail', 'category', 'instructor', 'instructor_name',
            'level', 'status', 'duration_hours', 'is_featured',
            'prerequisites', 'learning_objectives',
            'modules', 'resources',
            'total_videos', 'total_duration_minutes', 'enrolled_students_count',
            'is_enrolled', 'created_at', 'updated_at', 'published_at'
        ]
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(user=request.user).exists()
        return False


class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating courses."""
    
    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'description', 'short_description',
            'thumbnail', 'category', 'level', 'status',
            'duration_hours', 'is_featured', 'prerequisites', 'learning_objectives'
        ]
    
    def create(self, validated_data):
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for enrollments."""
    
    course = CourseListSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'user_email', 'user_name', 'course',
            'status', 'enrolled_at', 'completed_at', 'expires_at',
            'assigned_by', 'progress'
        ]
        read_only_fields = ['enrolled_at']
    
    def get_progress(self, obj):
        from progress.models import CourseProgress
        try:
            progress = CourseProgress.objects.get(user=obj.user, course=obj.course)
            return progress.progress_percentage
        except CourseProgress.DoesNotExist:
            return 0


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating enrollments."""
    
    class Meta:
        model = Enrollment
        fields = ['user', 'course', 'status', 'expires_at']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_admin:
            validated_data['assigned_by'] = request.user
        return super().create(validated_data)


class BulkEnrollmentSerializer(serializers.Serializer):
    """Serializer for bulk enrolling students."""
    
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    course_id = serializers.IntegerField()
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    
    def validate_course_id(self, value):
        try:
            Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found.")
        return value
