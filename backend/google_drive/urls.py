"""
URL patterns for Google Drive integration.
"""
from django.urls import path
from .views import (
    DriveConnectionStatusView,
    ListDriveFilesView,
    ListDriveFoldersView,
    GetDriveFileView,
    SearchDriveFilesView,
    GetVideoEmbedUrlView
)

app_name = 'google_drive'

urlpatterns = [
    path('status/', DriveConnectionStatusView.as_view(), name='connection_status'),
    path('files/', ListDriveFilesView.as_view(), name='list_files'),
    path('folders/', ListDriveFoldersView.as_view(), name='list_folders'),
    path('files/<str:file_id>/', GetDriveFileView.as_view(), name='get_file'),
    path('search/', SearchDriveFilesView.as_view(), name='search_files'),
    path('embed/<str:file_id>/', GetVideoEmbedUrlView.as_view(), name='embed_url'),
]
