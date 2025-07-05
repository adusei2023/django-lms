"""
User Views for LMS
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import UserProfile
from .forms import UserProfileForm, CustomUserCreationForm, UserUpdateForm

User = get_user_model()


class RegisterView(CreateView):
    """User registration view"""
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('users:profile')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        # Create user profile
        UserProfile.objects.create(user=user)
        # Log the user in
        login(self.request, user)
        messages.success(self.request, 'Registration successful!')
        return response


class ProfileView(LoginRequiredMixin, DetailView):
    """User profile view"""
    model = UserProfile
    template_name = 'users/profile.html'
    context_object_name = 'profile'
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get enrollment statistics
        enrollments = user.enrollments.all()
        context['enrollments_count'] = enrollments.count()
        context['completed_courses'] = enrollments.filter(completed_at__isnull=False).count()
        
        # Calculate total hours learned (mock calculation)
        context['hours_learned'] = enrollments.count() * 10  # Placeholder
        
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update user profile"""
    model = User
    form_class = UserUpdateForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user role"""
    try:
        profile = request.user.profile
        if request.user.user_type == 'instructor':
            return redirect('dashboard:instructor_dashboard')
        elif request.user.user_type == 'admin':
            return redirect('dashboard:dashboard')  # General dashboard for admin
        else:
            return redirect('dashboard:student_dashboard')
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        UserProfile.objects.create(user=request.user)
        return redirect('dashboard:student_dashboard')
        UserProfile.objects.create(user=request.user)
        return redirect('dashboard:student_dashboard')


def login_view(request):
    """Custom login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'users:dashboard_redirect')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('dashboard:home')
