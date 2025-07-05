"""
API Serializers for LMS
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import UserProfile
from courses.models import Course, Module, Lesson, Category, CourseReview, CourseResource
from enrollments.models import Enrollment, LessonProgress, ModuleProgress, Certificate
from quizzes.models import Quiz, Question, AnswerChoice, QuizAttempt, StudentAnswer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'role', 'bio', 'avatar', 'phone_number', 'date_of_birth', 
                 'location', 'timezone', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'icon', 'created_at']


class CourseResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseResource
        fields = ['id', 'title', 'file', 'resource_type', 'size', 'uploaded_at']


class LessonSerializer(serializers.ModelSerializer):
    resources = CourseResourceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'video_url', 'duration', 'order', 
                 'is_free', 'resources', 'created_at']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'lessons', 'created_at']


class CourseReviewSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    
    class Meta:
        model = CourseReview
        fields = ['id', 'student', 'rating', 'comment', 'created_at']
        read_only_fields = ['student', 'created_at']


class CourseListSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_students = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'thumbnail', 'price', 'level',
                 'instructor', 'category', 'average_rating', 'total_students',
                 'created_at', 'is_published']


class CourseDetailSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    reviews = CourseReviewSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_students = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'thumbnail', 'price', 'level',
                 'instructor', 'category', 'modules', 'reviews', 'average_rating',
                 'total_students', 'created_at', 'updated_at', 'is_published']


class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseListSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at', 'completed_at',
                 'progress_percentage', 'certificate_issued']


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = ['id', 'lesson', 'completed', 'time_spent', 'completed_at']


class ModuleProgressSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)
    lesson_progress = LessonProgressSerializer(many=True, read_only=True)
    
    class Meta:
        model = ModuleProgress
        fields = ['id', 'module', 'completed', 'completed_at', 'lesson_progress']


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    choices = AnswerChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'points', 'order', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    course = CourseListSerializer(read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'course', 'time_limit',
                 'max_attempts', 'passing_score', 'questions', 'created_at']


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['question', 'selected_choice', 'text_answer']


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    student = UserSerializer(read_only=True)
    answers = StudentAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'student', 'score', 'passed', 'started_at',
                 'completed_at', 'answers']


class CertificateSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True)
    
    class Meta:
        model = Certificate
        fields = ['id', 'enrollment', 'certificate_id', 'issued_at', 'pdf_file']
