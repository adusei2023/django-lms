"""
API ViewSets for LMS
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from users.models import UserProfile
from courses.models import Course, Module, Lesson, Category, CourseReview
from enrollments.models import Enrollment, LessonProgress, ModuleProgress
from quizzes.models import Quiz, QuizAttempt, StudentAnswer

from .serializers import (
    UserSerializer, UserProfileSerializer, CategorySerializer,
    CourseListSerializer, CourseDetailSerializer, CourseReviewSerializer,
    EnrollmentSerializer, LessonProgressSerializer, ModuleProgressSerializer,
    QuizSerializer, QuizAttemptSerializer, StudentAnswerSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own profile unless they're staff
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own profile unless they're staff
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.filter(status='published')
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='published')
        
        # Add annotations for average rating and total students
        queryset = queryset.annotate(
            average_rating=Avg('reviews__rating'),
            total_students=Count('enrollments')
        )
        
        # Filter by category if specified
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__id=category)
        
        # Filter by level if specified
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Search by title or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                description__icontains=search
            )
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        """Enroll the current user in a course"""
        course = self.get_object()
        
        # Check if user is already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {'error': 'You are already enrolled in this course'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            student=request.user,
            course=course
        )
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def review(self, request, pk=None):
        """Add a review for a course"""
        course = self.get_object()
        
        # Check if user is enrolled
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {'error': 'You must be enrolled in this course to review it'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has already reviewed
        if CourseReview.objects.filter(student=request.user, course=course).exists():
            return Response(
                {'error': 'You have already reviewed this course'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CourseReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user, course=course)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete_lesson(self, request, pk=None):
        """Mark a lesson as completed"""
        enrollment = self.get_object()
        lesson_id = request.data.get('lesson_id')
        
        if not lesson_id:
            return Response(
                {'error': 'lesson_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lesson = get_object_or_404(Lesson, id=lesson_id, module__course=enrollment.course)
        
        # Get or create lesson progress
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        if not lesson_progress.completed:
            lesson_progress.completed = True
            lesson_progress.save()
            
            # Check if module is now complete
            module = lesson.module
            module_progress, _ = ModuleProgress.objects.get_or_create(
                enrollment=enrollment,
                module=module
            )
            
            # Check if all lessons in module are completed
            total_lessons = module.lessons.count()
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment,
                lesson__module=module,
                completed=True
            ).count()
            
            if completed_lessons == total_lessons and not module_progress.completed:
                module_progress.completed = True
                module_progress.save()
        
        serializer = LessonProgressSerializer(lesson_progress)
        return Response(serializer.data)


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only show quizzes for courses the user is enrolled in
        enrolled_courses = Enrollment.objects.filter(
            student=self.request.user
        ).values_list('course', flat=True)
        
        return Quiz.objects.filter(course__in=enrolled_courses)
    
    @action(detail=True, methods=['post'])
    def start_attempt(self, request, pk=None):
        """Start a new quiz attempt"""
        quiz = self.get_object()
        
        # Check if user has reached max attempts
        attempt_count = QuizAttempt.objects.filter(
            student=request.user,
            quiz=quiz
        ).count()
        
        if attempt_count >= quiz.max_attempts:
            return Response(
                {'error': 'Maximum attempts reached'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new attempt
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz
        )
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def submit_attempt(self, request, pk=None):
        """Submit a quiz attempt"""
        quiz = self.get_object()
        attempt_id = request.data.get('attempt_id')
        answers = request.data.get('answers', [])
        
        attempt = get_object_or_404(
            QuizAttempt,
            id=attempt_id,
            student=request.user,
            quiz=quiz,
            completed_at__isnull=True
        )
        
        # Save answers
        total_score = 0
        max_score = 0
        
        for answer_data in answers:
            answer_serializer = StudentAnswerSerializer(data=answer_data)
            if answer_serializer.is_valid():
                answer = answer_serializer.save(attempt=attempt)
                
                # Calculate score
                question = answer.question
                max_score += question.points
                
                if question.question_type == 'multiple_choice':
                    if answer.selected_choice and answer.selected_choice.is_correct:
                        total_score += question.points
                elif question.question_type == 'true_false':
                    if answer.selected_choice and answer.selected_choice.is_correct:
                        total_score += question.points
        
        # Update attempt with score
        attempt.score = (total_score / max_score * 100) if max_score > 0 else 0
        attempt.passed = attempt.score >= quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.save()
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data)


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(student=self.request.user)
