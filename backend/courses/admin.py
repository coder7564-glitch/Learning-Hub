"""
Admin configuration for courses.
"""
from django.contrib import admin
from .models import Category, Course, Module, Video, Resource, Enrollment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    ordering = ('order',)


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    fk_name = 'course'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'level', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'level', 'is_featured', 'category')
    search_fields = ('title', 'description', 'instructor__email')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('instructor',)
    inlines = [ModuleInline, ResourceInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'short_description', 'thumbnail')
        }),
        ('Classification', {
            'fields': ('category', 'level', 'status', 'is_featured')
        }),
        ('Details', {
            'fields': ('instructor', 'duration_hours', 'prerequisites', 'learning_objectives')
        }),
        ('Dates', {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
    )


class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    ordering = ('order',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_published', 'created_at')
    list_filter = ('is_published', 'course')
    search_fields = ('title', 'course__title')
    inlines = [VideoInline]
    ordering = ('course', 'order')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'duration_minutes', 'order', 'is_preview', 'is_published')
    list_filter = ('is_published', 'is_preview', 'module__course')
    search_fields = ('title', 'module__title', 'module__course__title')
    ordering = ('module', 'order')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'course', 'module', 'order', 'is_published')
    list_filter = ('resource_type', 'is_published')
    search_fields = ('title', 'course__title', 'module__title')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'enrolled_at', 'completed_at', 'assigned_by')
    list_filter = ('status', 'course', 'enrolled_at')
    search_fields = ('user__email', 'course__title')
    raw_id_fields = ('user', 'course', 'assigned_by')
    date_hierarchy = 'enrolled_at'
