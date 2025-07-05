from django.contrib import admin
from django.utils.html import format_html
from .models import (
    DashboardSettings, ActivityLog, Announcement, AnnouncementView,
    StudyGoal, LearningPath, LearningPathCourse
)


@admin.register(DashboardSettings)
class DashboardSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'email_notifications', 'push_notifications', 'created_at')
    list_filter = ('theme', 'email_notifications', 'push_notifications', 'created_at')
    search_fields = ('user__username', 'user__email')
    raw_id_fields = ('user',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Display Preferences', {
            'fields': ('show_progress_charts', 'show_recent_activity', 'show_upcoming_deadlines', 'show_course_recommendations')
        }),
        ('Notification Preferences', {
            'fields': ('email_notifications', 'push_notifications', 'weekly_progress_email')
        }),
        ('Appearance', {
            'fields': ('theme',)
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'course', 'created_at')
    list_filter = ('action', 'created_at', 'course__category')
    search_fields = ('user__username', 'description', 'course__title')
    raw_id_fields = ('user', 'course')
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'action', 'description', 'course')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'course')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'announcement_type', 'priority', 'course', 'author', 'is_active', 'published_at', 'expires_at')
    list_filter = ('announcement_type', 'priority', 'is_active', 'published_at', 'course__category')
    search_fields = ('title', 'content', 'author__username')
    raw_id_fields = ('course', 'author')
    
    fieldsets = (
        ('Announcement Information', {
            'fields': ('title', 'content', 'announcement_type', 'priority')
        }),
        ('Targeting', {
            'fields': ('course', 'target_user_types')
        }),
        ('Scheduling', {
            'fields': ('is_active', 'published_at', 'expires_at')
        }),
        ('Settings', {
            'fields': ('author', 'is_dismissible')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'course')
    
    actions = ['activate_announcements', 'deactivate_announcements']
    
    def activate_announcements(self, request, queryset):
        queryset.update(is_active=True)
    activate_announcements.short_description = "Activate selected announcements"
    
    def deactivate_announcements(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_announcements.short_description = "Deactivate selected announcements"


@admin.register(AnnouncementView)
class AnnouncementViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'announcement', 'viewed_at', 'is_dismissed', 'dismissed_at')
    list_filter = ('is_dismissed', 'viewed_at', 'announcement__announcement_type')
    search_fields = ('user__username', 'announcement__title')
    raw_id_fields = ('user', 'announcement')
    
    readonly_fields = ('viewed_at', 'dismissed_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'announcement')


@admin.register(StudyGoal)
class StudyGoalAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'goal_type', 'progress_display', 'start_date', 'end_date', 'is_active', 'is_completed')
    list_filter = ('goal_type', 'is_active', 'is_completed', 'start_date', 'end_date')
    search_fields = ('student__username', 'title', 'description')
    raw_id_fields = ('student',)
    
    fieldsets = (
        ('Goal Information', {
            'fields': ('student', 'title', 'description', 'goal_type')
        }),
        ('Target & Progress', {
            'fields': ('target_value', 'current_value')
        }),
        ('Timeframe', {
            'fields': ('start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_active', 'is_completed', 'completed_at')
        }),
    )
    
    readonly_fields = ('completed_at',)
    
    def progress_display(self, obj):
        percentage = obj.progress_percentage
        color = 'green' if percentage >= 100 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}% ({}/{})</span>',
            color, percentage, obj.current_value, obj.target_value
        )
    progress_display.short_description = 'Progress'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student')


class LearningPathCourseInline(admin.TabularInline):
    model = LearningPathCourse
    extra = 0
    fields = ('course', 'order', 'is_required')
    raw_id_fields = ('course',)


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'course_count', 'progress_display', 'estimated_duration_weeks', 'is_active', 'created_at')
    list_filter = ('is_active', 'estimated_duration_weeks', 'created_at')
    search_fields = ('student__username', 'title', 'description')
    raw_id_fields = ('student',)
    inlines = [LearningPathCourseInline]
    
    fieldsets = (
        ('Learning Path Information', {
            'fields': ('student', 'title', 'description')
        }),
        ('Settings', {
            'fields': ('is_active', 'estimated_duration_weeks')
        }),
    )
    
    def course_count(self, obj):
        return obj.path_courses.count()
    course_count.short_description = 'Courses'
    
    def progress_display(self, obj):
        percentage = obj.progress_percentage
        color = 'green' if percentage >= 100 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, percentage
        )
    progress_display.short_description = 'Progress'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student').prefetch_related('path_courses')


@admin.register(LearningPathCourse)
class LearningPathCourseAdmin(admin.ModelAdmin):
    list_display = ('learning_path', 'course', 'order', 'is_required', 'progress_display')
    list_filter = ('is_required', 'course__category')
    search_fields = ('learning_path__title', 'course__title', 'learning_path__student__username')
    raw_id_fields = ('learning_path', 'course')
    
    def progress_display(self, obj):
        percentage = obj.get_progress_percentage()
        color = 'green' if percentage >= 100 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color, percentage
        )
    progress_display.short_description = 'Progress'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('learning_path__student', 'course')
