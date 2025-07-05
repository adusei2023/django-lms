from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Course listing and browsing
    path('', views.CourseListView.as_view(), name='course_list'),
    path('category/<slug:slug>/', views.CategoryListView.as_view(), name='category_courses'),
    
    # Course details and enrollment
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/enroll/', views.enroll_course, name='enroll_course'),
    path('<int:course_pk>/review/', views.add_review, name='add_review'),
    
    # Lesson views
    path('lesson/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('lesson/<int:pk>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
]
