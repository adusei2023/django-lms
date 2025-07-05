from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from courses.models import Course
from .models import Enrollment, LessonProgress

@login_required
def enroll_in_course(request, course_id):
    """Enroll user in a course"""
    course = get_object_or_404(Course, id=course_id, status='published')
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=course.slug)
    
    # Create enrollment
    enrollment = Enrollment.objects.create(
        student=request.user,
        course=course,
        status='active'
    )
    
    messages.success(request, f'Successfully enrolled in {course.title}!')
    return redirect('courses:course_detail', slug=course.slug)

@login_required
def unenroll_from_course(request, course_id):
    """Unenroll user from a course"""
    course = get_object_or_404(Course, id=course_id)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    enrollment.delete()
    messages.success(request, f'Successfully unenrolled from {course.title}.')
    return redirect('courses:course_list')

@login_required
def my_courses(request):
    """Display user's enrolled courses"""
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    return render(request, 'enrollments/my_courses.html', {
        'enrollments': enrollments
    })

@login_required
def enrollment_progress(request, enrollment_id):
    """Display enrollment progress"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    progress = LessonProgress.objects.filter(enrollment=enrollment).select_related('lesson')
    
    return render(request, 'enrollments/progress.html', {
        'enrollment': enrollment,
        'progress': progress
    })

@login_required
def generate_certificate(request, enrollment_id):
    """Generate certificate for completed course"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    
    if enrollment.progress_percentage < 100:
        messages.error(request, 'Course must be 100% complete to generate certificate.')
        return redirect('enrollments:progress', enrollment_id=enrollment_id)
    
    # In a real implementation, you would generate a PDF certificate here
    messages.success(request, 'Certificate generated successfully!')
    return render(request, 'enrollments/certificate.html', {
        'enrollment': enrollment
    })

def enrollment_list(request):
    """Placeholder view for enrollments"""
    return render(request, 'enrollments/enrollment_list.html')
