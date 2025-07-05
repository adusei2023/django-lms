from django.urls import path
from . import views
from .health import HealthCheckView

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Student dashboard
    path('student/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    
    # Instructor dashboard
    path('instructor/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    
    # Health check for AWS
    path('health/', HealthCheckView.as_view(), name='health_check'),
]
