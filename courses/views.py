"""
Course Views for LMS
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator

from .models import Course, Category, Module, Lesson, CourseReview
from enrollments.models import Enrollment, LessonProgress


class CourseListView(ListView):
    """List all published courses"""
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        return Course.objects.filter(status='published').select_related('instructor', 'category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category')
        context['current_level'] = self.request.GET.get('level')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class CourseDetailView(DetailView):
    """Course detail view"""
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_queryset(self):
        return Course.objects.filter(status='published').select_related('instructor', 'category').prefetch_related('modules__lessons', 'reviews__student')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        # Calculate course statistics
        context['average_rating'] = course.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        context['total_reviews'] = course.reviews.count()
        context['total_students'] = course.enrollments.count()
        
        # Check if user is enrolled
        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user,
                course=course
            ).exists()
            
            # If enrolled, get progress
            if context['is_enrolled']:
                enrollment = Enrollment.objects.get(student=self.request.user, course=course)
                context['enrollment'] = enrollment
                context['progress_percentage'] = enrollment.progress_percentage
        
        # Course modules and lessons
        context['modules'] = course.modules.prefetch_related('lessons').order_by('order')
        
        # Related courses
        context['related_courses'] = Course.objects.filter(
            category=course.category,
            status='published'
        ).exclude(id=course.id)[:4]
        
        return context


@login_required
def enroll_course(request, pk):
    """Enroll user in a course"""
    course = get_object_or_404(Course, pk=pk, status='published')
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
    else:
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f'Successfully enrolled in {course.title}!')
    
    return redirect('courses:course_detail', pk=course.pk)


class LessonDetailView(LoginRequiredMixin, DetailView):
    """Lesson detail view"""
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'
    
    def get_object(self):
        lesson = get_object_or_404(
            Lesson,
            pk=self.kwargs['pk'],
            module__course__status='published'
        )
        
        # Check if user is enrolled in the course
        if not Enrollment.objects.filter(
            student=self.request.user,
            course=lesson.module.course
        ).exists():
            messages.error(self.request, 'You must be enrolled in this course to view lessons.')
            return redirect('courses:course_detail', pk=lesson.module.course.pk)
        
        return lesson
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        course = lesson.module.course
        
        # Get enrollment and progress
        enrollment = Enrollment.objects.get(student=self.request.user, course=course)
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        context['course'] = course
        context['module'] = lesson.module
        context['enrollment'] = enrollment
        context['lesson_progress'] = lesson_progress
        
        # Get all lessons in the course for navigation
        all_lessons = []
        for module in course.modules.order_by('order'):
            for lesson_item in module.lessons.order_by('order'):
                all_lessons.append(lesson_item)
        
        context['all_lessons'] = all_lessons
        
        # Find previous and next lessons
        try:
            current_index = all_lessons.index(lesson)
            context['previous_lesson'] = all_lessons[current_index - 1] if current_index > 0 else None
            context['next_lesson'] = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
        except ValueError:
            context['previous_lesson'] = None
            context['next_lesson'] = None
        
        return context


@login_required
def mark_lesson_complete(request, pk):
    """Mark a lesson as completed"""
    lesson = get_object_or_404(Lesson, pk=pk)
    
    # Check enrollment
    try:
        enrollment = Enrollment.objects.get(student=request.user, course=lesson.module.course)
    except Enrollment.DoesNotExist:
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('courses:course_detail', pk=lesson.module.course.pk)
    
    # Mark lesson as complete
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    if not lesson_progress.completed:
        lesson_progress.completed = True
        lesson_progress.save()
        messages.success(request, f'Lesson "{lesson.title}" marked as completed!')
    
    return redirect('courses:lesson_detail', pk=lesson.pk)


class CategoryListView(ListView):
    """List courses by category"""
    model = Course
    template_name = 'courses/category_courses.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Course.objects.filter(
            category=self.category,
            status='published'
        ).select_related('instructor').annotate(
            average_rating=Avg('reviews__rating'),
            total_students=Count('enrollments')
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


@login_required
def add_review(request, course_pk):
    """Add a review for a course"""
    course = get_object_or_404(Course, pk=course_pk, status='published')
    
    # Check if user is enrolled
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'You must be enrolled in this course to leave a review.')
        return redirect('courses:course_detail', pk=course.pk)
    
    # Check if user has already reviewed
    if CourseReview.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'You have already reviewed this course.')
        return redirect('courses:course_detail', pk=course.pk)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            CourseReview.objects.create(
                student=request.user,
                course=course,
                rating=int(rating),
                comment=comment
            )
            messages.success(request, 'Review added successfully!')
        else:
            messages.error(request, 'Please provide both rating and comment.')
    
    return redirect('courses:course_detail', pk=course.pk)
