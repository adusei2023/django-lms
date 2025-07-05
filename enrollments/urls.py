from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('enroll/<int:course_id>/', views.enroll_in_course, name='enroll'),
    path('unenroll/<int:course_id>/', views.unenroll_from_course, name='unenroll'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('progress/<int:enrollment_id>/', views.enrollment_progress, name='progress'),
    path('certificate/<int:enrollment_id>/', views.generate_certificate, name='certificate'),
]
