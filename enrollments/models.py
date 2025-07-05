from django.db import models
from django.conf import settings
from django.utils import timezone
from courses.models import Course, Lesson, Module


class Enrollment(models.Model):
    """Student enrollment in courses"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('suspended', 'Suspended'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'user_type': 'student'}
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Enrollment tracking
    enrolled_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    # Progress tracking
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    
    # Payment information (for paid courses)
    payment_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    # Certificates
    certificate_issued = models.BooleanField(default=False)
    certificate_issued_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"
    
    def mark_as_started(self):
        """Mark the enrollment as started when first lesson is accessed"""
        if not self.started_at:
            self.started_at = timezone.now()
            self.save(update_fields=['started_at'])
    
    def mark_as_completed(self):
        """Mark the enrollment as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress_percentage = 100.00
        self.save(update_fields=['status', 'completed_at', 'progress_percentage'])
    
    def calculate_progress(self):
        """Calculate and update progress percentage"""
        total_lessons = self.course.total_lessons
        if total_lessons == 0:
            self.progress_percentage = 0.00
        else:
            completed_lessons = self.lesson_progress.filter(is_completed=True).count()
            self.progress_percentage = (completed_lessons / total_lessons) * 100
        
        self.save(update_fields=['progress_percentage'])
        
        # Auto-complete if all lessons are done
        if self.progress_percentage >= 100 and self.status == 'active':
            self.mark_as_completed()
    
    def get_next_lesson(self):
        """Get the next lesson the student should take"""
        # Get all lessons in order
        all_lessons = []
        for module in self.course.modules.filter(is_published=True).order_by('order'):
            all_lessons.extend(module.lessons.filter(is_published=True).order_by('order'))
        
        # Find first incomplete lesson
        for lesson in all_lessons:
            progress, created = LessonProgress.objects.get_or_create(
                enrollment=self,
                lesson=lesson,
                defaults={'is_completed': False}
            )
            if not progress.is_completed:
                return lesson
        
        return None
    
    def get_completed_lessons_count(self):
        """Get number of completed lessons"""
        return self.lesson_progress.filter(is_completed=True).count()
    
    def get_total_study_time(self):
        """Get total time spent studying in minutes"""
        return self.lesson_progress.aggregate(
            total_time=models.Sum('time_spent_minutes')
        )['total_time'] or 0


class LessonProgress(models.Model):
    """Track student progress for individual lessons"""
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='student_progress')
    
    # Progress tracking
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    
    # Video progress (for video lessons)
    video_progress_seconds = models.PositiveIntegerField(default=0, help_text="Progress in video in seconds")
    
    # Engagement tracking
    first_accessed = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    access_count = models.PositiveIntegerField(default=1)
    
    # Notes and bookmarks
    notes = models.TextField(blank=True, help_text="Student's personal notes for this lesson")
    is_bookmarked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['enrollment', 'lesson']
        ordering = ['lesson__module__order', 'lesson__order']
    
    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.enrollment.student.username} - {self.lesson.title}"
    
    def mark_as_completed(self):
        """Mark lesson as completed and update enrollment progress"""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save(update_fields=['is_completed', 'completed_at'])
            
            # Update enrollment progress
            self.enrollment.calculate_progress()
    
    def add_study_time(self, minutes):
        """Add study time to the lesson"""
        self.time_spent_minutes += minutes
        self.save(update_fields=['time_spent_minutes'])
    
    def update_video_progress(self, seconds):
        """Update video watching progress"""
        self.video_progress_seconds = max(self.video_progress_seconds, seconds)
        self.save(update_fields=['video_progress_seconds'])


class ModuleProgress(models.Model):
    """Track student progress for course modules"""
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='student_progress')
    
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    first_accessed = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['enrollment', 'module']
        ordering = ['module__order']
    
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.module.title}"
    
    def calculate_progress(self):
        """Calculate module progress based on lesson completion"""
        total_lessons = self.module.lessons.filter(is_published=True).count()
        if total_lessons == 0:
            self.progress_percentage = 100.00
        else:
            completed_lessons = self.enrollment.lesson_progress.filter(
                lesson__module=self.module,
                is_completed=True
            ).count()
            self.progress_percentage = (completed_lessons / total_lessons) * 100
        
        # Mark as completed if all lessons are done
        if self.progress_percentage >= 100 and not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
        
        self.save(update_fields=['progress_percentage', 'is_completed', 'completed_at'])


class StudentNote(models.Model):
    """Student notes for lessons"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_notes'
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='student_notes')
    content = models.TextField()
    timestamp_seconds = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Timestamp in video where note was taken (in seconds)"
    )
    is_public = models.BooleanField(default=False, help_text="Share note with other students")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.lesson.title} note"


class Certificate(models.Model):
    """Course completion certificates"""
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_id = models.CharField(max_length=100, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', null=True, blank=True)
    
    # Certificate details
    student_name = models.CharField(max_length=200)
    course_title = models.CharField(max_length=200)
    instructor_name = models.CharField(max_length=200)
    completion_date = models.DateField()
    
    is_valid = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"Certificate - {self.student_name} - {self.course_title}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_id:
            import uuid
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
