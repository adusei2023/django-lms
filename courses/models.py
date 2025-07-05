from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from PIL import Image
import uuid


class Category(models.Model):
    """Course categories for better organization"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """Main course model"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    PRICE_TYPE_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, help_text="Brief description for course cards")
    
    # Relationships
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        limit_choices_to={'user_type': 'instructor'}
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Media
    cover_image = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    intro_video = models.FileField(upload_to='course_intros/', null=True, blank=True)
    
    # Course Details
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_weeks = models.PositiveIntegerField(help_text="Estimated duration in weeks")
    estimated_hours = models.PositiveIntegerField(help_text="Estimated total hours to complete")
    
    # Pricing
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES, default='free')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    max_students = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of students (leave blank for unlimited)")
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    meta_keywords = models.CharField(max_length=200, blank=True, help_text="SEO keywords, comma-separated")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        # Resize cover image
        if self.cover_image:
            img = Image.open(self.cover_image.path)
            if img.height > 400 or img.width > 600:
                output_size = (600, 400)
                img.thumbnail(output_size)
                img.save(self.cover_image.path)
    
    def get_absolute_url(self):
        return reverse('courses:course_detail', kwargs={'slug': self.slug})
    
    @property
    def total_lessons(self):
        return sum(module.lessons.count() for module in self.modules.all())
    
    @property
    def total_duration_minutes(self):
        return sum(lesson.duration_minutes for lesson in self.get_all_lessons() if lesson.duration_minutes)
    
    @property
    def enrollment_count(self):
        return self.enrollments.filter(is_active=True).count()
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_all_lessons(self):
        """Get all lessons across all modules"""
        from itertools import chain
        return list(chain(*[module.lessons.all() for module in self.modules.all()]))
    
    def is_free(self):
        return self.price_type == 'free' or self.price == 0


class Module(models.Model):
    """Course modules/sections"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """Individual lessons within modules"""
    LESSON_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text/Article'),
        ('pdf', 'PDF Document'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='video')
    
    # Content
    content = models.TextField(blank=True, help_text="Text content for the lesson")
    video_file = models.FileField(upload_to='lesson_videos/', null=True, blank=True)
    video_url = models.URLField(blank=True, help_text="External video URL (YouTube, Vimeo, etc.)")
    pdf_file = models.FileField(upload_to='lesson_pdfs/', null=True, blank=True)
    
    # Metadata
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Lesson duration in minutes")
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False, help_text="Can be viewed without enrollment")
    is_published = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['module', 'order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('courses:lesson_detail', kwargs={
            'course_slug': self.module.course.slug,
            'lesson_slug': self.slug
        })


class CourseReview(models.Model):
    """Student reviews for courses"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_reviews'
    )
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['course', 'student']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.rating}/5)"


class CourseResource(models.Model):
    """Additional resources for courses"""
    RESOURCE_TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('link', 'External Link'),
        ('file', 'File Download'),
        ('video', 'Video'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    file = models.FileField(upload_to='course_resources/', null=True, blank=True)
    url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False, help_text="Available to non-enrolled students")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
