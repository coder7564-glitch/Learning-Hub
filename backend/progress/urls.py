"""
URL patterns for progress tracking.
"""
from django.urls import path
from .views import (
    MyCourseProgressListView, CourseProgressDetailView,
    UpdateVideoProgressView, VideoProgressListView,
    MyCertificatesView, CertificateDetailView, IssueCertificateView,
    StudentProgressReportView, CourseProgressReportView
)

app_name = 'progress'

urlpatterns = [
    # Student Progress
    path('my-progress/', MyCourseProgressListView.as_view(), name='my_progress'),
    path('courses/<slug:course_slug>/', CourseProgressDetailView.as_view(), name='course_progress'),
    path('courses/<slug:course_slug>/videos/', VideoProgressListView.as_view(), name='video_progress_list'),
    path('video/update/', UpdateVideoProgressView.as_view(), name='update_video_progress'),
    
    # Certificates
    path('certificates/', MyCertificatesView.as_view(), name='my_certificates'),
    path('certificates/<str:certificate_number>/', CertificateDetailView.as_view(), name='certificate_detail'),
    path('courses/<slug:course_slug>/certificate/', IssueCertificateView.as_view(), name='issue_certificate'),
    
    # Admin Reports
    path('reports/students/', StudentProgressReportView.as_view(), name='student_progress_report'),
    path('reports/courses/<slug:course_slug>/', CourseProgressReportView.as_view(), name='course_progress_report'),
]
