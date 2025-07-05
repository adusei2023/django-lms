from django.db import models
from django.conf import settings
from django.utils import timezone
from courses.models import Course


class DashboardSettings(models.Model):
    """User dashboard customization settings"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_settings'
    )
    
    # Display preferences
    show_progress_charts = models.BooleanField(default=True)
    show_recent_activity = models.BooleanField(default=True)
    show_upcoming_deadlines = models.BooleanField(default=True)
    show_course_recommendations = models.BooleanField(default=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    weekly_progress_email = models.BooleanField(default=True)
    
    # Layout preferences
    theme = models.CharField(
        max_length=20,
        choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')],
        default='light'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Dashboard Settings"


class ActivityLog(models.Model):
    """Track user activities for dashboard display"""
    ACTION_CHOICES = [
        ('login', 'Logged in'),
        ('logout', 'Logged out'),
        ('course_enrolled', 'Enrolled in course'),
        ('course_completed', 'Completed course'),
        ('lesson_completed', 'Completed lesson'),
        ('quiz_attempted', 'Attempted quiz'),
        ('quiz_passed', 'Passed quiz'),
        ('certificate_earned', 'Earned certificate'),
        ('profile_updated', 'Updated profile'),
        ('course_created', 'Created course'),
        ('course_updated', 'Updated course'),
        ('lesson_created', 'Created lesson'),
        ('student_graded', 'Graded student'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    
    # Related objects (optional)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"


class Announcement(models.Model):
    """System-wide or course-specific announcements"""
    ANNOUNCEMENT_TYPE_CHOICES = [
        ('system', 'System-wide'),
        ('course', 'Course-specific'),
        ('maintenance', 'Maintenance'),
        ('feature', 'New Feature'),
        ('policy', 'Policy Update'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPE_CHOICES, default='system')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Targeting
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='announcements')
    target_user_types = models.CharField(
        max_length=100,
        default='student,instructor,admin',
        help_text="Comma-separated list of user types (student, instructor, admin)"
    )
    
    # Scheduling
    is_active = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Author
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements_created'
    )
    
    # Engagement
    is_dismissible = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['is_active', 'published_at']),
            models.Index(fields=['course', 'is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def is_visible_to_user(self, user):
        """Check if announcement is visible to a specific user"""
        if not self.is_active:
            return False
        
        # Check expiration
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        
        # Check user type targeting
        target_types = [t.strip() for t in self.target_user_types.split(',')]
        if user.user_type not in target_types:
            return False
        
        # Check course-specific targeting
        if self.course and user.user_type == 'student':
            return user.enrollments.filter(course=self.course, is_active=True).exists()
        elif self.course and user.user_type == 'instructor':
            return self.course.instructor == user
        
        return True


class AnnouncementView(models.Model):
    """Track which users have viewed announcements"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcement_views'
    )
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='views'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    is_dismissed = models.BooleanField(default=False)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'announcement']
    
    def __str__(self):
        return f"{self.user.username} viewed {self.announcement.title}"


class StudyGoal(models.Model):
    """Student study goals and tracking"""
    GOAL_TYPE_CHOICES = [
        ('daily_minutes', 'Daily Study Time'),
        ('weekly_lessons', 'Weekly Lessons'),
        ('monthly_courses', 'Monthly Course Completion'),
        ('custom', 'Custom Goal'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='study_goals',
        limit_choices_to={'user_type': 'student'}
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    
    # Goal parameters
    target_value = models.PositiveIntegerField(help_text="Target number (minutes, lessons, courses, etc.)")
    current_value = models.PositiveIntegerField(default=0)
    
    # Timeframe
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    
    # Status
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.title}"
    
    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(100, (self.current_value / self.target_value) * 100)
    
    def update_progress(self, value):
        """Update goal progress"""
        self.current_value = value
        
        if self.current_value >= self.target_value and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
        
        self.save()


class LearningPath(models.Model):
    """Personalized learning paths for students"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_paths',
        limit_choices_to={'user_type': 'student'}
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    courses = models.ManyToManyField(Course, through='LearningPathCourse')
    
    # Metadata
    is_active = models.BooleanField(default=True)
    estimated_duration_weeks = models.PositiveIntegerField(help_text="Estimated weeks to complete")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.title}"
    
    @property
    def progress_percentage(self):
        """Calculate overall progress through the learning path"""
        path_courses = self.path_courses.all()
        if not path_courses:
            return 0
        
        total_progress = sum(
            pc.get_progress_percentage() for pc in path_courses
        )
        return total_progress / len(path_courses)


class LearningPathCourse(models.Model):
    """Courses within a learning path with ordering"""
    learning_path = models.ForeignKey(
        LearningPath,
        on_delete=models.CASCADE,
        related_name='path_courses'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['learning_path', 'course']
    
    def __str__(self):
        return f"{self.learning_path.title} - {self.course.title}"
    
    def get_progress_percentage(self):
        """Get student's progress in this course"""
        enrollment = self.learning_path.student.enrollments.filter(
            course=self.course,
            is_active=True
        ).first()
        
        if enrollment:
            return float(enrollment.progress_percentage)
        return 0
