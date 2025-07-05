from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Course, Module, Lesson, CourseReview, CourseResource


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'course_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def course_count(self, obj):
        return obj.course_set.count()
    course_count.short_description = 'Courses'


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ('title', 'order', 'is_published')
    ordering = ('order',)


class CourseResourceInline(admin.TabularInline):
    model = CourseResource
    extra = 0
    fields = ('title', 'resource_type', 'order', 'is_public')
    ordering = ('order',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'status', 'difficulty_level', 'price_type', 'enrollment_count', 'is_featured', 'created_at')
    list_filter = ('status', 'difficulty_level', 'price_type', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'description', 'instructor__username', 'instructor__email')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('instructor',)
    inlines = [ModuleInline, CourseResourceInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description', 'instructor', 'category')
        }),
        ('Media', {
            'fields': ('cover_image', 'intro_video'),
            'classes': ('collapse',)
        }),
        ('Course Details', {
            'fields': ('difficulty_level', 'duration_weeks', 'estimated_hours', 'max_students')
        }),
        ('Pricing', {
            'fields': ('price_type', 'price')
        }),
        ('Status & Features', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('instructor', 'category').prefetch_related('enrollments')
    
    def enrollment_count(self, obj):
        return obj.enrollment_count
    enrollment_count.short_description = 'Enrollments'
    
    actions = ['make_featured', 'remove_featured', 'publish_courses', 'draft_courses']
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = "Mark selected courses as featured"
    
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
    remove_featured.short_description = "Remove featured status"
    
    def publish_courses(self, request, queryset):
        queryset.update(status='published')
    publish_courses.short_description = "Publish selected courses"
    
    def draft_courses(self, request, queryset):
        queryset.update(status='draft')
    draft_courses.short_description = "Move to draft"


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('title', 'lesson_type', 'order', 'is_preview', 'is_published', 'duration_minutes')
    ordering = ('order',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'lesson_count', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at', 'course__category')
    search_fields = ('title', 'description', 'course__title')
    raw_id_fields = ('course',)
    inlines = [LessonInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course').prefetch_related('lessons')
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Lessons'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'lesson_type', 'order', 'duration_minutes', 'is_preview', 'is_published', 'created_at')
    list_filter = ('lesson_type', 'is_preview', 'is_published', 'created_at', 'module__course__category')
    search_fields = ('title', 'content', 'module__title', 'module__course__title')
    raw_id_fields = ('module',)
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'slug', 'lesson_type', 'order')
        }),
        ('Content', {
            'fields': ('content', 'video_file', 'video_url', 'pdf_file')
        }),
        ('Settings', {
            'fields': ('duration_minutes', 'is_preview', 'is_published')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('module', 'module__course')


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating', 'title', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at', 'course__category')
    search_fields = ('title', 'comment', 'course__title', 'student__username')
    raw_id_fields = ('course', 'student')
    
    actions = ['approve_reviews', 'unapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"
    
    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_reviews.short_description = "Unapprove selected reviews"


@admin.register(CourseResource)
class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'resource_type', 'order', 'is_public', 'created_at')
    list_filter = ('resource_type', 'is_public', 'created_at', 'course__category')
    search_fields = ('title', 'description', 'course__title')
    raw_id_fields = ('course',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description', 'resource_type', 'order')
        }),
        ('Content', {
            'fields': ('file', 'url')
        }),
        ('Settings', {
            'fields': ('is_public',)
        }),
    )
