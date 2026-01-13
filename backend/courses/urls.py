"""
URL patterns for courses.
"""
from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView,
    CourseListView, CourseDetailView, FeaturedCoursesView,
    ModuleListCreateView, ModuleDetailView,
    VideoListCreateView, VideoDetailView,
    ResourceListCreateView, ResourceDetailView,
    EnrollmentListView, EnrollmentCreateView, EnrollmentDetailView,
    SelfEnrollView, BulkEnrollView, MarkCourseCompleteView,
    MyCoursesView
)

app_name = 'courses'

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    
    # Courses
    path('', CourseListView.as_view(), name='course_list'),
    path('featured/', FeaturedCoursesView.as_view(), name='featured_courses'),
    path('<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
    
    # Modules
    path('<slug:course_slug>/modules/', ModuleListCreateView.as_view(), name='module_list'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(), name='module_detail'),
    
    # Videos
    path('modules/<int:module_id>/videos/', VideoListCreateView.as_view(), name='video_list'),
    path('videos/<int:pk>/', VideoDetailView.as_view(), name='video_detail'),
    
    # Resources
    path('<slug:course_slug>/resources/', ResourceListCreateView.as_view(), name='resource_list'),
    path('resources/<int:pk>/', ResourceDetailView.as_view(), name='resource_detail'),
    
    # Enrollments
    path('enrollments/', EnrollmentListView.as_view(), name='enrollment_list'),
    path('enrollments/create/', EnrollmentCreateView.as_view(), name='enrollment_create'),
    path('enrollments/<int:pk>/', EnrollmentDetailView.as_view(), name='enrollment_detail'),
    path('enrollments/bulk/', BulkEnrollView.as_view(), name='bulk_enroll'),
    path('enrollments/<int:enrollment_id>/complete/', MarkCourseCompleteView.as_view(), name='mark_complete'),
    
    # Student specific
    path('<slug:course_slug>/enroll/', SelfEnrollView.as_view(), name='self_enroll'),
    path('my-courses/', MyCoursesView.as_view(), name='my_courses'),
]
