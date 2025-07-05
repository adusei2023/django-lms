from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from courses.models import Course
from enrollments.models import Enrollment
from dashboard.models import Announcement

User = get_user_model()


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Simple context without complex queries for now
        context['featured_courses'] = []
        context['total_courses'] = 0
        context['total_students'] = 0
        context['total_instructors'] = 0
        
        return context
        
        # Get recent announcements
        context['recent_announcements'] = Announcement.objects.filter(
            is_active=True,
            announcement_type='system'
        ).order_by('-published_at')[:3]
        
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view - redirects based on user type"""
    
    def get(self, request, *args, **kwargs):
        if request.user.is_student():
            return redirect('dashboard:student_dashboard')
        elif request.user.is_instructor():
            return redirect('dashboard:instructor_dashboard')
        else:
            return redirect('admin:index')


class StudentDashboardView(LoginRequiredMixin, TemplateView):
    """Student dashboard"""
    template_name = 'dashboard/student_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get student enrollments
        enrollments = Enrollment.objects.filter(
            student=self.request.user,
            is_active=True
        ).select_related('course', 'course__instructor')
        
        context['enrollments'] = enrollments
        context['in_progress_courses'] = enrollments.filter(
            status='active',
            progress_percentage__lt=100
        )
        context['completed_courses'] = enrollments.filter(status='completed')
        
        return context


class InstructorDashboardView(LoginRequiredMixin, TemplateView):
    """Instructor dashboard"""
    template_name = 'dashboard/instructor_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get instructor courses
        courses = Course.objects.filter(
            instructor=self.request.user
        ).prefetch_related('enrollments')
        
        context['courses'] = courses
        context['total_students'] = sum(
            course.enrollments.filter(is_active=True).count() 
            for course in courses
        )
        
        return context


# Simple views for testing
def handler404(request, exception):
    """Custom 404 page"""
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """Custom 500 page"""
    return render(request, 'errors/500.html', status=500)
