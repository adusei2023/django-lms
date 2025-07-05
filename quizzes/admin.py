from django.contrib import admin
from django.utils.html import format_html
from .models import Quiz, Question, AnswerChoice, QuizAttempt, StudentAnswer, QuizFeedback


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 2
    fields = ('text', 'is_correct', 'order')


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    fields = ('text', 'question_type', 'points', 'order', 'explanation')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'quiz_type', 'total_questions', 'total_points', 'pass_percentage', 'is_published', 'created_at')
    list_filter = ('quiz_type', 'is_published', 'created_at', 'course__category')
    search_fields = ('title', 'description', 'course__title')
    raw_id_fields = ('course', 'module', 'lesson')
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'quiz_type', 'course', 'module', 'lesson')
        }),
        ('Quiz Settings', {
            'fields': ('time_limit_minutes', 'max_attempts', 'pass_percentage')
        }),
        ('Display Options', {
            'fields': ('show_correct_answers', 'show_explanations', 'randomize_questions', 'randomize_answers')
        }),
        ('Availability', {
            'fields': ('is_published', 'available_from', 'available_until')
        }),
        ('Ordering', {
            'fields': ('order',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course').prefetch_related('questions')
    
    actions = ['publish_quizzes', 'unpublish_quizzes']
    
    def publish_quizzes(self, request, queryset):
        queryset.update(is_published=True)
    publish_quizzes.short_description = "Publish selected quizzes"
    
    def unpublish_quizzes(self, request, queryset):
        queryset.update(is_published=False)
    unpublish_quizzes.short_description = "Unpublish selected quizzes"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'text_preview', 'question_type', 'points', 'order', 'created_at')
    list_filter = ('question_type', 'created_at', 'quiz__course__category')
    search_fields = ('text', 'explanation', 'quiz__title')
    raw_id_fields = ('quiz',)
    inlines = [AnswerChoiceInline]
    
    fieldsets = (
        ('Question Information', {
            'fields': ('quiz', 'question_type', 'text', 'explanation', 'image')
        }),
        ('Scoring & Order', {
            'fields': ('points', 'order')
        }),
    )
    
    def text_preview(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Question Text'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz')


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text_preview', 'is_correct', 'order', 'created_at')
    list_filter = ('is_correct', 'created_at', 'question__question_type')
    search_fields = ('text', 'question__text', 'question__quiz__title')
    raw_id_fields = ('question',)
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Choice Text'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question__quiz')


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    fields = ('question', 'selected_choice', 'text_answer', 'points_earned', 'is_auto_graded')
    readonly_fields = ('question', 'is_auto_graded')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'attempt_number', 'status', 'score', 'percentage', 'passed', 'started_at', 'submitted_at')
    list_filter = ('status', 'passed', 'started_at', 'quiz__course__category')
    search_fields = ('student__username', 'student__email', 'quiz__title')
    raw_id_fields = ('student', 'quiz')
    inlines = [StudentAnswerInline]
    
    fieldsets = (
        ('Attempt Information', {
            'fields': ('student', 'quiz', 'attempt_number', 'status')
        }),
        ('Timing', {
            'fields': ('started_at', 'submitted_at', 'time_taken_minutes')
        }),
        ('Scoring', {
            'fields': ('score', 'max_score', 'percentage', 'passed')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('started_at', 'submitted_at', 'time_taken_minutes', 'score', 'max_score', 'percentage', 'passed')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'quiz')
    
    actions = ['grade_attempts', 'reset_attempts']
    
    def grade_attempts(self, request, queryset):
        for attempt in queryset:
            if attempt.status == 'completed':
                attempt.submit()
    grade_attempts.short_description = "Re-grade selected attempts"
    
    def reset_attempts(self, request, queryset):
        queryset.update(status='in_progress')
    reset_attempts.short_description = "Reset to in progress"


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_choice', 'points_earned', 'is_auto_graded', 'created_at')
    list_filter = ('is_auto_graded', 'created_at', 'question__question_type')
    search_fields = ('attempt__student__username', 'question__text', 'text_answer')
    raw_id_fields = ('attempt', 'question', 'selected_choice', 'graded_by')
    
    fieldsets = (
        ('Answer Information', {
            'fields': ('attempt', 'question', 'selected_choice', 'text_answer')
        }),
        ('Grading', {
            'fields': ('is_auto_graded', 'points_earned', 'instructor_feedback', 'graded_by', 'graded_at')
        }),
    )
    
    readonly_fields = ('is_auto_graded', 'graded_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('attempt__student', 'question', 'selected_choice')


@admin.register(QuizFeedback)
class QuizFeedbackAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'instructor', 'created_at')
    list_filter = ('created_at', 'attempt__quiz__course__category')
    search_fields = ('attempt__student__username', 'general_feedback', 'instructor__username')
    raw_id_fields = ('attempt', 'instructor')
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('attempt', 'instructor')
        }),
        ('Feedback Content', {
            'fields': ('general_feedback', 'strengths', 'areas_for_improvement')
        }),
        ('Recommendations', {
            'fields': ('recommended_resources', 'next_steps')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('attempt__student', 'instructor')
