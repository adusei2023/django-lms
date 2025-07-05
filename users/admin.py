from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'user_type', 'first_name', 'last_name', 'is_email_verified', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'is_email_verified', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'avatar', 'bio', 'date_of_birth', 'phone_number', 'is_email_verified')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'email', 'first_name', 'last_name')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'instructor_id', 'department', 'location')
    list_filter = ('department', 'location')
    search_fields = ('user__username', 'user__email', 'student_id', 'instructor_id', 'department')
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'github_url', 'website_url'),
            'classes': ('collapse',)
        }),
        ('Location & Timezone', {
            'fields': ('location', 'timezone')
        }),
        ('Student Information', {
            'fields': ('student_id', 'enrollment_date'),
            'classes': ('collapse',)
        }),
        ('Instructor Information', {
            'fields': ('instructor_id', 'department', 'specialization', 'years_of_experience'),
            'classes': ('collapse',)
        }),
    )
