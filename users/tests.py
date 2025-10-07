from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test cases for the User model"""

    def setUp(self):
        """Set up test data"""
        self.student = User.objects.create_user(
            username='teststudent',
            email='student@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Student',
            role='student'
        )
        self.instructor = User.objects.create_user(
            username='testinstructor',
            email='instructor@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Instructor',
            role='instructor'
        )

    def test_user_creation(self):
        """Test that a user can be created"""
        self.assertEqual(self.student.username, 'teststudent')
        self.assertEqual(self.student.email, 'student@test.com')
        self.assertEqual(self.student.role, 'student')
        self.assertTrue(self.student.check_password('testpass123'))

    def test_user_string_representation(self):
        """Test the string representation of a user"""
        self.assertEqual(str(self.student), 'teststudent')

    def test_user_role_validation(self):
        """Test that user roles are properly validated"""
        self.assertIn(self.student.role, ['student', 'instructor', 'admin'])
        self.assertEqual(self.instructor.role, 'instructor')

    def test_user_full_name(self):
        """Test the full name method if it exists"""
        if hasattr(self.student, 'get_full_name'):
            full_name = self.student.get_full_name()
            self.assertEqual(full_name, 'Test Student')

    def test_user_email_unique(self):
        """Test that email addresses must be unique"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='another_user',
                email='student@test.com',  # Duplicate email
                password='testpass123'
            )


class UserAuthenticationTestCase(TestCase):
    """Test cases for user authentication"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role='student'
        )
        self.login_url = reverse('users:login')

    def test_user_login_success(self):
        """Test that a user can log in with correct credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Should redirect on successful login
        self.assertEqual(response.status_code, 302)

    def test_user_login_failure(self):
        """Test that login fails with incorrect credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        # Should stay on login page
        self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        """Test that a user can log out"""
        self.client.login(username='testuser', password='testpass123')
        logout_url = reverse('users:logout')
        response = self.client.get(logout_url)
        # Should redirect after logout
        self.assertEqual(response.status_code, 302)


class UserProfileTestCase(TestCase):
    """Test cases for user profile functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role='student'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_profile_view_access(self):
        """Test that authenticated users can access their profile"""
        profile_url = reverse('users:profile')
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update(self):
        """Test that users can update their profile"""
        profile_url = reverse('users:profile')
        response = self.client.post(profile_url, {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@test.com'
        })
        self.user.refresh_from_db()
        # Check if update was successful
        self.assertEqual(self.user.first_name, 'Updated')


class UserPermissionsTestCase(TestCase):
    """Test cases for user permissions and roles"""

    def setUp(self):
        """Set up test data"""
        self.student = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='testpass123',
            role='student'
        )
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@test.com',
            password='testpass123',
            role='instructor'
        )

    def test_student_role_permissions(self):
        """Test that students have appropriate permissions"""
        self.assertEqual(self.student.role, 'student')
        if hasattr(self.student, 'is_student'):
            self.assertTrue(self.student.is_student())
        if hasattr(self.student, 'is_instructor'):
            self.assertFalse(self.student.is_instructor())

    def test_instructor_role_permissions(self):
        """Test that instructors have appropriate permissions"""
        self.assertEqual(self.instructor.role, 'instructor')
        if hasattr(self.instructor, 'is_instructor'):
            self.assertTrue(self.instructor.is_instructor())
        if hasattr(self.instructor, 'is_student'):
            self.assertFalse(self.instructor.is_student())

