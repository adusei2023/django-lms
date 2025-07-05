from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Category, Course, Module, Lesson
from enrollments.models import Enrollment
from quizzes.models import Quiz, Question, AnswerChoice
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create users
        self.create_users()
        
        # Create categories
        self.create_categories()
        
        # Create courses
        self.create_courses()
        
        # Create enrollments
        self.create_enrollments()
        
        # Create quizzes
        self.create_quizzes()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))

    def create_users(self):
        self.stdout.write('Creating users...')
        
        # Create instructors
        instructor1 = User.objects.create_user(
            username='john_instructor',
            email='john@example.com',
            password='password123',
            first_name='John',
            last_name='Smith',
            user_type='instructor',
            bio='Experienced software developer and teacher with 10 years of experience.'
        )
        
        instructor2 = User.objects.create_user(
            username='jane_instructor',
            email='jane@example.com',
            password='password123',
            first_name='Jane',
            last_name='Doe',
            user_type='instructor',
            bio='Data scientist and machine learning expert.'
        )
        
        # Create students
        for i in range(1, 11):
            User.objects.create_user(
                username=f'student{i}',
                email=f'student{i}@example.com',
                password='password123',
                first_name=f'Student',
                last_name=f'{i}',
                user_type='student'
            )
        
        self.stdout.write(self.style.SUCCESS('Users created'))

    def create_categories(self):
        self.stdout.write('Creating categories...')
        
        categories = [
            {'name': 'Web Development', 'description': 'Learn to build websites and web applications'},
            {'name': 'Data Science', 'description': 'Analyze data and build machine learning models'},
            {'name': 'Mobile Development', 'description': 'Create mobile apps for iOS and Android'},
            {'name': 'DevOps', 'description': 'Learn deployment, CI/CD, and infrastructure'},
            {'name': 'UI/UX Design', 'description': 'Design beautiful and user-friendly interfaces'},
        ]
        
        for cat_data in categories:
            Category.objects.create(
                name=cat_data['name'],
                description=cat_data['description'],
                slug=slugify(cat_data['name'])
            )
        
        self.stdout.write(self.style.SUCCESS('Categories created'))

    def create_courses(self):
        self.stdout.write('Creating courses...')
        
        instructors = User.objects.filter(user_type='instructor')
        categories = Category.objects.all()
        
        courses_data = [
            {
                'title': 'Complete Python Web Development with Django',
                'description': 'Learn to build full-stack web applications using Django framework',
                'short_description': 'Master Django development from basics to advanced concepts',
                'difficulty_level': 'intermediate',
                'duration_weeks': 12,
                'estimated_hours': 40,
                'price': Decimal('99.99'),
                'category': 'Web Development'
            },
            {
                'title': 'Data Science with Python',
                'description': 'Complete data science course covering statistics, machine learning, and data visualization',
                'short_description': 'Learn data science from scratch with Python',
                'difficulty_level': 'beginner',
                'duration_weeks': 16,
                'estimated_hours': 60,
                'price': Decimal('149.99'),
                'category': 'Data Science'
            },
            {
                'title': 'React Native Mobile Development',
                'description': 'Build cross-platform mobile apps using React Native',
                'short_description': 'Create mobile apps for iOS and Android',
                'difficulty_level': 'intermediate',
                'duration_weeks': 10,
                'estimated_hours': 35,
                'price': Decimal('79.99'),
                'category': 'Mobile Development'
            },
            {
                'title': 'Introduction to Programming',
                'description': 'Learn programming fundamentals using Python',
                'short_description': 'Perfect for complete beginners',
                'difficulty_level': 'beginner',
                'duration_weeks': 8,
                'estimated_hours': 20,
                'price': Decimal('0.00'),
                'price_type': 'free',
                'category': 'Web Development'
            },
        ]
        
        for course_data in courses_data:
            category = categories.get(name=course_data['category'])
            instructor = random.choice(instructors)
            
            course = Course.objects.create(
                title=course_data['title'],
                description=course_data['description'],
                short_description=course_data['short_description'],
                instructor=instructor,
                category=category,
                difficulty_level=course_data['difficulty_level'],
                duration_weeks=course_data['duration_weeks'],
                estimated_hours=course_data['estimated_hours'],
                price=course_data['price'],
                price_type=course_data.get('price_type', 'paid'),
                status='published',
                is_featured=random.choice([True, False]),
                slug=slugify(course_data['title'])
            )
            
            # Create modules for each course
            self.create_modules_for_course(course)
        
        self.stdout.write(self.style.SUCCESS('Courses created'))

    def create_modules_for_course(self, course):
        modules_count = random.randint(3, 6)
        
        for i in range(1, modules_count + 1):
            module = Module.objects.create(
                course=course,
                title=f'Module {i}: {course.title} - Part {i}',
                description=f'This module covers important concepts for {course.title}',
                order=i
            )
            
            # Create lessons for each module
            self.create_lessons_for_module(module)

    def create_lessons_for_module(self, module):
        lessons_count = random.randint(3, 8)
        lesson_types = ['video', 'text', 'pdf']
        
        for i in range(1, lessons_count + 1):
            lesson_type = random.choice(lesson_types)
            
            Lesson.objects.create(
                module=module,
                title=f'Lesson {i}: {module.title} - Topic {i}',
                lesson_type=lesson_type,
                content=f'This is the content for lesson {i} of {module.title}. It covers important concepts and practical examples.',
                duration_minutes=random.randint(10, 45),
                order=i,
                is_preview=i == 1,  # First lesson is preview
                slug=slugify(f'lesson-{i}-{module.title}-topic-{i}')
            )

    def create_enrollments(self):
        self.stdout.write('Creating enrollments...')
        
        students = User.objects.filter(user_type='student')
        courses = Course.objects.all()
        
        # Create random enrollments
        for student in students:
            # Each student enrolls in 2-4 courses
            student_courses = random.sample(list(courses), random.randint(2, min(4, len(courses))))
            
            for course in student_courses:
                enrollment = Enrollment.objects.create(
                    student=student,
                    course=course,
                    status='active',
                    progress_percentage=Decimal(random.uniform(0, 100))
                )
                
                # Some enrollments are completed
                if random.random() < 0.3:  # 30% chance of completion
                    enrollment.mark_as_completed()
        
        self.stdout.write(self.style.SUCCESS('Enrollments created'))

    def create_quizzes(self):
        self.stdout.write('Creating quizzes...')
        
        courses = Course.objects.all()
        
        for course in courses:
            # Create 1-2 quizzes per course
            quizzes_count = random.randint(1, 2)
            
            for i in range(1, quizzes_count + 1):
                quiz = Quiz.objects.create(
                    title=f'{course.title} - Quiz {i}',
                    description=f'Test your knowledge of {course.title}',
                    course=course,
                    quiz_type='graded',
                    time_limit_minutes=30,
                    max_attempts=3,
                    pass_percentage=Decimal('70.00'),
                    is_published=True
                )
                
                # Create questions for each quiz
                self.create_questions_for_quiz(quiz)
        
        self.stdout.write(self.style.SUCCESS('Quizzes created'))

    def create_questions_for_quiz(self, quiz):
        questions_count = random.randint(5, 10)
        
        for i in range(1, questions_count + 1):
            question = Question.objects.create(
                quiz=quiz,
                question_type='multiple_choice',
                text=f'Question {i}: What is the main concept covered in {quiz.title}?',
                explanation=f'This question tests your understanding of key concepts in {quiz.course.title}.',
                points=1,
                order=i
            )
            
            # Create answer choices
            choices = [
                {'text': 'Correct answer', 'is_correct': True},
                {'text': 'Incorrect answer 1', 'is_correct': False},
                {'text': 'Incorrect answer 2', 'is_correct': False},
                {'text': 'Incorrect answer 3', 'is_correct': False},
            ]
            
            for j, choice_data in enumerate(choices):
                AnswerChoice.objects.create(
                    question=question,
                    text=choice_data['text'],
                    is_correct=choice_data['is_correct'],
                    order=j + 1
                )
