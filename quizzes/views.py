"""
Quiz Views for LMS
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction

from .models import Quiz, QuizAttempt, Question, StudentAnswer
from enrollments.models import Enrollment


class QuizListView(LoginRequiredMixin, ListView):
    """List all quizzes for enrolled courses"""
    model = Quiz
    template_name = 'quizzes/quiz_list.html'
    context_object_name = 'quizzes'
    
    def get_queryset(self):
        # Only show quizzes for courses the user is enrolled in
        enrolled_courses = Enrollment.objects.filter(
            student=self.request.user
        ).values_list('course', flat=True)
        
        return Quiz.objects.filter(course__in=enrolled_courses).select_related('course')


class QuizDetailView(LoginRequiredMixin, DetailView):
    """Quiz detail and start view"""
    model = Quiz
    template_name = 'quizzes/quiz_detail.html'
    context_object_name = 'quiz'
    
    def get_object(self):
        quiz = get_object_or_404(Quiz, pk=self.kwargs['pk'])
        
        # Check if user is enrolled in the course
        if not Enrollment.objects.filter(
            student=self.request.user,
            course=quiz.course
        ).exists():
            messages.error(self.request, 'You must be enrolled in this course to take quizzes.')
            return redirect('courses:course_detail', pk=quiz.course.pk)
        
        return quiz
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.object
        
        # Get user's attempts
        attempts = QuizAttempt.objects.filter(
            student=self.request.user,
            quiz=quiz
        ).order_by('-started_at')
        
        context['attempts'] = attempts
        context['attempts_remaining'] = max(0, quiz.max_attempts - attempts.count())
        context['can_attempt'] = attempts.count() < quiz.max_attempts
        
        # Get best score
        if attempts.exists():
            context['best_score'] = max(attempt.score for attempt in attempts if attempt.score is not None)
        
        return context


@login_required
def start_quiz(request, pk):
    """Start a new quiz attempt"""
    quiz = get_object_or_404(Quiz, pk=pk)
    
    # Check enrollment
    if not Enrollment.objects.filter(student=request.user, course=quiz.course).exists():
        messages.error(request, 'You must be enrolled in this course to take quizzes.')
        return redirect('courses:course_detail', pk=quiz.course.pk)
    
    # Check attempt limit
    attempts_count = QuizAttempt.objects.filter(student=request.user, quiz=quiz).count()
    if attempts_count >= quiz.max_attempts:
        messages.error(request, 'You have reached the maximum number of attempts for this quiz.')
        return redirect('quizzes:quiz_detail', pk=quiz.pk)
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        student=request.user,
        quiz=quiz
    )
    
    return redirect('quizzes:take_quiz', pk=attempt.pk)


class TakeQuizView(LoginRequiredMixin, DetailView):
    """Take quiz view"""
    model = QuizAttempt
    template_name = 'quizzes/take_quiz.html'
    context_object_name = 'attempt'
    
    def get_object(self):
        attempt = get_object_or_404(
            QuizAttempt,
            pk=self.kwargs['pk'],
            student=self.request.user,
            completed_at__isnull=True
        )
        return attempt
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt = self.object
        
        # Get questions with choices
        questions = attempt.quiz.questions.prefetch_related('choices').order_by('order')
        context['questions'] = questions
        
        # Calculate time remaining
        if attempt.quiz.time_limit:
            elapsed_time = timezone.now() - attempt.started_at
            time_remaining = attempt.quiz.time_limit * 60 - elapsed_time.total_seconds()
            context['time_remaining'] = max(0, int(time_remaining))
        
        return context


@login_required
def submit_quiz(request, pk):
    """Submit quiz attempt"""
    if request.method != 'POST':
        return redirect('quizzes:quiz_list')
    
    attempt = get_object_or_404(
        QuizAttempt,
        pk=pk,
        student=request.user,
        completed_at__isnull=True
    )
    
    with transaction.atomic():
        total_score = 0
        max_score = 0
        
        # Process answers
        for question in attempt.quiz.questions.all():
            answer_key = f'question_{question.pk}'
            max_score += question.points
            
            if question.question_type in ['multiple_choice', 'true_false']:
                choice_id = request.POST.get(answer_key)
                if choice_id:
                    try:
                        choice = question.choices.get(pk=choice_id)
                        StudentAnswer.objects.create(
                            attempt=attempt,
                            question=question,
                            selected_choice=choice
                        )
                        if choice.is_correct:
                            total_score += question.points
                    except:
                        pass
            elif question.question_type == 'short_answer':
                text_answer = request.POST.get(answer_key, '').strip()
                if text_answer:
                    StudentAnswer.objects.create(
                        attempt=attempt,
                        question=question,
                        text_answer=text_answer
                    )
                    # For short answer, instructor needs to grade manually
                    # For now, give partial credit
                    total_score += question.points * 0.5
        
        # Calculate final score
        attempt.score = (total_score / max_score * 100) if max_score > 0 else 0
        attempt.passed = attempt.score >= attempt.quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.save()
    
    messages.success(request, f'Quiz submitted! You scored {attempt.score:.1f}%')
    return redirect('quizzes:quiz_result', pk=attempt.pk)


class QuizResultView(LoginRequiredMixin, DetailView):
    """View quiz results"""
    model = QuizAttempt
    template_name = 'quizzes/quiz_result.html'
    context_object_name = 'attempt'
    
    def get_object(self):
        return get_object_or_404(
            QuizAttempt,
            pk=self.kwargs['pk'],
            student=self.request.user,
            completed_at__isnull=False
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt = self.object
        
        # Get questions with user answers
        questions_with_answers = []
        for question in attempt.quiz.questions.order_by('order'):
            try:
                user_answer = StudentAnswer.objects.get(attempt=attempt, question=question)
            except StudentAnswer.DoesNotExist:
                user_answer = None
            
            questions_with_answers.append({
                'question': question,
                'user_answer': user_answer,
                'correct_answer': question.choices.filter(is_correct=True).first() if question.question_type in ['multiple_choice', 'true_false'] else None
            })
        
        context['questions_with_answers'] = questions_with_answers
        context['total_questions'] = attempt.quiz.questions.count()
        context['correct_answers'] = sum(1 for qa in questions_with_answers if qa['user_answer'] and qa['correct_answer'] and qa['user_answer'].selected_choice == qa['correct_answer'])
        
        return context
