"""
Views for Google Drive integration.
"""
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .services import GoogleDriveService
from accounts.permissions import IsAdmin


class DriveConnectionStatusView(APIView):
    """Check if user has connected Google Drive."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        connected = bool(user.google_access_token)
        
        return Response({
            'connected': connected,
            'email': user.email if connected else None
        })


class ListDriveFilesView(APIView):
    """List files from user's Google Drive."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get(self, request):
        folder_id = request.query_params.get('folder_id')
        file_type = request.query_params.get('type', 'video')
        page_token = request.query_params.get('page_token')
        
        service = GoogleDriveService(user=request.user)
        result = service.list_files(
            folder_id=folder_id,
            file_type=file_type,
            page_token=page_token
        )
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result)


class ListDriveFoldersView(APIView):
    """List folders from user's Google Drive."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get(self, request):
        parent_id = request.query_params.get('parent_id')
        
        service = GoogleDriveService(user=request.user)
        result = service.list_folders(parent_id=parent_id)
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result)


class GetDriveFileView(APIView):
    """Get a specific file from Google Drive."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get(self, request, file_id):
        service = GoogleDriveService(user=request.user)
        result = service.get_file(file_id)
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result)


class SearchDriveFilesView(APIView):
    """Search for files in Google Drive."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        file_type = request.query_params.get('type', 'video')
        
        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = GoogleDriveService(user=request.user)
        result = service.search_files(query=query, file_type=file_type)
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(result)


class GetVideoEmbedUrlView(APIView):
    """Get embeddable URL for a video."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, file_id):
        service = GoogleDriveService(user=request.user)
        embed_url = service.get_embed_url(file_id)
        
        return Response({'embed_url': embed_url})
