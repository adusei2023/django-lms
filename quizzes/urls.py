from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('', views.QuizListView.as_view(), name='quiz_list'),
    path('<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('<int:pk>/start/', views.start_quiz, name='start_quiz'),
    path('<int:pk>/take/', views.TakeQuizView.as_view(), name='take_quiz'),
    path('<int:pk>/submit/', views.submit_quiz, name='submit_quiz'),
    path('<int:pk>/results/', views.QuizResultView.as_view(), name='quiz_results'),
]
