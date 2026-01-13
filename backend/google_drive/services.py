"""
Google Drive API service for managing video content.
"""
import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings


class GoogleDriveService:
    """Service class for interacting with Google Drive API."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]
    
    def __init__(self, user=None):
        """Initialize the service with user credentials."""
        self.user = user
        self.service = None
        
        if user and user.google_access_token:
            self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the Google Drive service with user credentials."""
        try:
            creds = Credentials(
                token=self.user.google_access_token,
                refresh_token=self.user.google_refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                scopes=self.SCOPES
            )
            
            # Refresh token if expired
            if self.user.google_token_expiry and datetime.now() >= self.user.google_token_expiry:
                if creds.refresh_token:
                    creds.refresh(Request())
                    self.user.google_access_token = creds.token
                    self.user.google_token_expiry = datetime.now() + timedelta(hours=1)
                    self.user.save()
            
            self.service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            print(f"Error initializing Google Drive service: {e}")
            self.service = None
    
    def list_files(self, folder_id=None, file_type='video', page_size=50, page_token=None):
        """List files from Google Drive."""
        if not self.service:
            return {'error': 'Google Drive service not initialized'}
        
        try:
            query_parts = ["trashed = false"]
            
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            
            if file_type == 'video':
                query_parts.append("mimeType contains 'video/'")
            elif file_type == 'document':
                query_parts.append("(mimeType contains 'application/pdf' or mimeType contains 'document')")
            elif file_type == 'folder':
                query_parts.append("mimeType = 'application/vnd.google-apps.folder'")
            
            query = " and ".join(query_parts)
            
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, size, thumbnailLink, webViewLink, webContentLink, createdTime, modifiedTime, videoMediaMetadata)"
            ).execute()
            
            files = results.get('files', [])
            next_page_token = results.get('nextPageToken')
            
            return {
                'files': self._format_files(files),
                'next_page_token': next_page_token
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_file(self, file_id):
        """Get a single file's metadata from Google Drive."""
        if not self.service:
            return {'error': 'Google Drive service not initialized'}
        
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, thumbnailLink, webViewLink, webContentLink, createdTime, modifiedTime, videoMediaMetadata"
            ).execute()
            
            return self._format_file(file)
        except Exception as e:
            return {'error': str(e)}
    
    def search_files(self, query, file_type='video', page_size=20):
        """Search for files in Google Drive."""
        if not self.service:
            return {'error': 'Google Drive service not initialized'}
        
        try:
            query_parts = [f"name contains '{query}'", "trashed = false"]
            
            if file_type == 'video':
                query_parts.append("mimeType contains 'video/'")
            elif file_type == 'document':
                query_parts.append("(mimeType contains 'application/pdf' or mimeType contains 'document')")
            
            search_query = " and ".join(query_parts)
            
            results = self.service.files().list(
                q=search_query,
                pageSize=page_size,
                fields="files(id, name, mimeType, size, thumbnailLink, webViewLink, webContentLink, videoMediaMetadata)"
            ).execute()
            
            files = results.get('files', [])
            
            return {'files': self._format_files(files)}
        except Exception as e:
            return {'error': str(e)}
    
    def list_folders(self, parent_id=None):
        """List folders from Google Drive."""
        return self.list_files(folder_id=parent_id, file_type='folder')
    
    def get_embed_url(self, file_id):
        """Get embeddable URL for a video."""
        return f"https://drive.google.com/file/d/{file_id}/preview"
    
    def get_download_url(self, file_id):
        """Get download URL for a file."""
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    
    def _format_files(self, files):
        """Format a list of files."""
        return [self._format_file(f) for f in files]
    
    def _format_file(self, file):
        """Format a single file's data."""
        formatted = {
            'id': file.get('id'),
            'name': file.get('name'),
            'mime_type': file.get('mimeType'),
            'size': file.get('size'),
            'thumbnail_url': file.get('thumbnailLink'),
            'view_url': file.get('webViewLink'),
            'download_url': file.get('webContentLink'),
            'embed_url': self.get_embed_url(file.get('id')),
            'created_at': file.get('createdTime'),
            'modified_at': file.get('modifiedTime'),
        }
        
        # Add video metadata if available
        video_meta = file.get('videoMediaMetadata')
        if video_meta:
            formatted['duration_ms'] = video_meta.get('durationMillis')
            formatted['width'] = video_meta.get('width')
            formatted['height'] = video_meta.get('height')
            
            # Calculate duration in minutes
            if video_meta.get('durationMillis'):
                formatted['duration_minutes'] = int(int(video_meta['durationMillis']) / 60000)
        
        return formatted
