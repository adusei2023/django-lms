from django.db import models
from django.conf import settings
from django.utils import timezone
from courses.models import Course, Module, Lesson
import uuid


class Quiz(models.Model):
    """Quiz model for assessments"""
    QUIZ_TYPE_CHOICES = [
        ('practice', 'Practice Quiz'),
        ('graded', 'Graded Assessment'),
        ('final', 'Final Exam'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES, default='practice')
    
    # Relationships
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    
    # Quiz settings
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Time limit in minutes (leave blank for no limit)")
    max_attempts = models.PositiveIntegerField(default=3, help_text="Maximum number of attempts allowed")
    pass_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=70.00, help_text="Minimum percentage to pass")
    
    # Display settings
    show_correct_answers = models.BooleanField(default=True, help_text="Show correct answers after completion")
    show_explanations = models.BooleanField(default=True, help_text="Show explanations for answers")
    randomize_questions = models.BooleanField(default=False, help_text="Randomize question order")
    randomize_answers = models.BooleanField(default=False, help_text="Randomize answer choices")
    
    # Availability
    is_published = models.BooleanField(default=False)
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = "Quizzes"
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def total_questions(self):
        return self.questions.count()
    
    @property
    def total_points(self):
        return sum(q.points for q in self.questions.all())
    
    def is_available(self):
        """Check if quiz is currently available"""
        now = timezone.now()
        if self.available_from and now < self.available_from:
            return False
        if self.available_until and now > self.available_until:
            return False
        return self.is_published
    
    def get_attempts_left(self, student):
        """Get remaining attempts for a student"""
        attempts_used = self.attempts.filter(student=student).count()
        return max(0, self.max_attempts - attempts_used)
    
    def can_retake(self, student):
        """Check if student can retake the quiz"""
        return self.get_attempts_left(student) > 0


class Question(models.Model):
    """Quiz questions"""
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='multiple_choice')
    
    # Question content
    text = models.TextField(help_text="The question text")
    explanation = models.TextField(blank=True, help_text="Explanation shown after answering")
    image = models.ImageField(upload_to='question_images/', null=True, blank=True)
    
    # Scoring
    points = models.PositiveIntegerField(default=1)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"
    
    def get_correct_answers(self):
        """Get all correct answer choices"""
        return self.answer_choices.filter(is_correct=True)


class AnswerChoice(models.Model):
    """Answer choices for multiple choice questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.question} - {self.text[:50]}"


class QuizAttempt(models.Model):
    """Student quiz attempts"""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('timed_out', 'Timed Out'),
        ('abandoned', 'Abandoned'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    
    # Attempt details
    attempt_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_taken_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Scoring
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_score = models.PositiveIntegerField(null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    passed = models.BooleanField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['student', 'quiz', 'attempt_number']
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} (Attempt {self.attempt_number})"
    
    def save(self, *args, **kwargs):
        if not self.attempt_number:
            # Set attempt number
            last_attempt = QuizAttempt.objects.filter(
                student=self.student,
                quiz=self.quiz
            ).order_by('-attempt_number').first()
            
            self.attempt_number = 1 if not last_attempt else last_attempt.attempt_number + 1
        
        super().save(*args, **kwargs)
    
    def submit(self):
        """Submit the quiz attempt and calculate score"""
        if self.status != 'in_progress':
            return
        
        self.status = 'completed'
        self.submitted_at = timezone.now()
        
        # Calculate time taken
        time_diff = self.submitted_at - self.started_at
        self.time_taken_minutes = int(time_diff.total_seconds() / 60)
        
        # Calculate score
        total_score = 0
        max_possible = 0
        
        for answer in self.student_answers.all():
            max_possible += answer.question.points
            if answer.is_correct():
                total_score += answer.question.points
        
        self.score = total_score
        self.max_score = max_possible
        self.percentage = (total_score / max_possible * 100) if max_possible > 0 else 0
        self.passed = self.percentage >= self.quiz.pass_percentage
        
        self.save()
    
    def is_timed_out(self):
        """Check if attempt has timed out"""
        if not self.quiz.time_limit_minutes or self.status != 'in_progress':
            return False
        
        time_elapsed = timezone.now() - self.started_at
        return time_elapsed.total_seconds() > (self.quiz.time_limit_minutes * 60)
    
    def get_remaining_time_seconds(self):
        """Get remaining time in seconds"""
        if not self.quiz.time_limit_minutes or self.status != 'in_progress':
            return None
        
        time_elapsed = timezone.now() - self.started_at
        total_allowed = self.quiz.time_limit_minutes * 60
        return max(0, total_allowed - int(time_elapsed.total_seconds()))


class StudentAnswer(models.Model):
    """Student answers to quiz questions"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    
    # Answer data
    selected_choice = models.ForeignKey(
        AnswerChoice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="For multiple choice questions"
    )
    text_answer = models.TextField(blank=True, help_text="For text/essay questions")
    
    # Auto-grading
    is_auto_graded = models.BooleanField(default=True)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Manual grading (for essay questions)
    instructor_feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_answers'
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt.student.username} - {self.question}"
    
    def is_correct(self):
        """Check if the answer is correct"""
        if self.question.question_type == 'multiple_choice':
            return self.selected_choice and self.selected_choice.is_correct
        elif self.question.question_type == 'true_false':
            return self.selected_choice and self.selected_choice.is_correct
        else:
            # For text/essay questions, manual grading required
            return self.points_earned == self.question.points
    
    def auto_grade(self):
        """Auto-grade the answer if possible"""
        if self.question.question_type in ['multiple_choice', 'true_false']:
            if self.is_correct():
                self.points_earned = self.question.points
            else:
                self.points_earned = 0
            self.save()


class QuizFeedback(models.Model):
    """Instructor feedback on quiz attempts"""
    attempt = models.OneToOneField(QuizAttempt, on_delete=models.CASCADE, related_name='feedback')
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_feedback_given'
    )
    
    # Feedback
    general_feedback = models.TextField(help_text="General feedback on the attempt")
    strengths = models.TextField(blank=True, help_text="What the student did well")
    areas_for_improvement = models.TextField(blank=True, help_text="Areas where student can improve")
    
    # Recommendations
    recommended_resources = models.TextField(blank=True, help_text="Suggested additional resources")
    next_steps = models.TextField(blank=True, help_text="Suggested next steps for learning")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Feedback for {self.attempt.student.username} - {self.attempt.quiz.title}"
