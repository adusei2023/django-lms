from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Enrollment, LessonProgress, ModuleProgress, StudentNote, Certificate


class LessonProgressInline(admin.TabularInline):
    model = LessonProgress
    extra = 0
    fields = ('lesson', 'is_completed', 'completed_at', 'time_spent_minutes', 'is_bookmarked')
    readonly_fields = ('completed_at',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'progress_percentage', 'enrolled_at', 'completed_at', 'certificate_issued')
    list_filter = ('status', 'is_active', 'certificate_issued', 'enrolled_at', 'course__category')
    search_fields = ('student__username', 'student__email', 'course__title')
    raw_id_fields = ('student', 'course')
    inlines = [LessonProgressInline]
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'course', 'status', 'is_active')
        }),
        ('Progress Tracking', {
            'fields': ('progress_percentage', 'enrolled_at', 'started_at', 'completed_at', 'last_accessed')
        }),
        ('Payment Information', {
            'fields': ('payment_amount', 'payment_date', 'payment_method', 'transaction_id'),
            'classes': ('collapse',)
        }),
        ('Certificate', {
            'fields': ('certificate_issued', 'certificate_issued_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('enrolled_at', 'started_at', 'completed_at', 'last_accessed', 'certificate_issued_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'course')
    
    actions = ['activate_enrollments', 'complete_enrollments', 'issue_certificates']
    
    def activate_enrollments(self, request, queryset):
        queryset.update(is_active=True, status='active')
    activate_enrollments.short_description = "Activate selected enrollments"
    
    def complete_enrollments(self, request, queryset):
        for enrollment in queryset:
            enrollment.mark_as_completed()
    complete_enrollments.short_description = "Mark as completed"
    
    def issue_certificates(self, request, queryset):
        queryset.update(certificate_issued=True)
    issue_certificates.short_description = "Issue certificates"


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'completed_at', 'time_spent_minutes', 'is_bookmarked')
    list_filter = ('is_completed', 'is_bookmarked', 'completed_at', 'lesson__lesson_type')
    search_fields = ('enrollment__student__username', 'lesson__title', 'lesson__module__title')
    raw_id_fields = ('enrollment', 'lesson')
    
    fieldsets = (
        ('Progress Information', {
            'fields': ('enrollment', 'lesson', 'is_completed', 'completed_at')
        }),
        ('Time Tracking', {
            'fields': ('time_spent_minutes', 'video_progress_seconds')
        }),
        ('Engagement', {
            'fields': ('access_count', 'is_bookmarked', 'notes')
        }),
    )
    
    readonly_fields = ('first_accessed', 'last_accessed', 'completed_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('enrollment__student', 'lesson')


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'module', 'is_completed', 'progress_percentage', 'completed_at')
    list_filter = ('is_completed', 'completed_at', 'module__course__category')
    search_fields = ('enrollment__student__username', 'module__title', 'module__course__title')
    raw_id_fields = ('enrollment', 'module')
    
    readonly_fields = ('first_accessed', 'last_accessed', 'completed_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('enrollment__student', 'module')


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'timestamp_seconds', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'lesson__lesson_type')
    search_fields = ('student__username', 'lesson__title', 'content')
    raw_id_fields = ('student', 'lesson')
    
    fieldsets = (
        ('Note Information', {
            'fields': ('student', 'lesson', 'content')
        }),
        ('Settings', {
            'fields': ('timestamp_seconds', 'is_public')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'lesson')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'student_name', 'course_title', 'completion_date', 'is_valid', 'issued_at')
    list_filter = ('is_valid', 'issued_at', 'completion_date')
    search_fields = ('certificate_id', 'student_name', 'course_title', 'enrollment__student__username')
    raw_id_fields = ('enrollment',)
    
    fieldsets = (
        ('Certificate Information', {
            'fields': ('enrollment', 'certificate_id', 'pdf_file')
        }),
        ('Certificate Details', {
            'fields': ('student_name', 'course_title', 'instructor_name', 'completion_date')
        }),
        ('Status', {
            'fields': ('is_valid',)
        }),
    )
    
    readonly_fields = ('certificate_id', 'issued_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('enrollment__student', 'enrollment__course')
