"""
Custom permissions for accounts.
"""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Permission class that only allows admins."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsStudent(permissions.BasePermission):
    """Permission class that only allows students."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_student


class IsAdminOrSelf(permissions.BasePermission):
    """Permission class that allows admins or the user themselves."""
    
    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or obj == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Permission class that allows read access to all, write access to admins."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsEnrolledOrAdmin(permissions.BasePermission):
    """Permission that allows access if user is enrolled in course or is admin."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        # Check if user is enrolled in the course
        return obj.enrollments.filter(user=request.user).exists()
