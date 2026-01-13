"""
Admin configuration for accounts.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, AdminProfile


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'


class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = 'Admin Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_picture', 'bio', 'phone_number')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Google OAuth', {'fields': ('google_access_token', 'google_refresh_token', 'google_token_expiry')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )
    
    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == User.Role.STUDENT:
                return [StudentProfileInline]
            elif obj.role == User.Role.ADMIN:
                return [AdminProfileInline]
        return []


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'department', 'enrollment_date')
    search_fields = ('user__email', 'student_id', 'department')
    list_filter = ('department', 'enrollment_date')


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'can_manage_users', 'can_manage_courses', 'can_view_reports')
    search_fields = ('user__email', 'department')
    list_filter = ('can_manage_users', 'can_manage_courses', 'can_view_reports')
