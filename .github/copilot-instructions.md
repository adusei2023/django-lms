<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# LMS (Learning Management System) - Django Project

This is a comprehensive Learning Management System built with Django 4.x, designed for scalable deployment on AWS Elastic Beanstalk.

## Project Structure

### Apps and Responsibilities:
- **users**: Custom user authentication, profiles, and role management (Student, Instructor, Admin)
- **courses**: Course creation, management, modules, and lessons
- **enrollments**: Student enrollment tracking, progress monitoring, and certificates
- **quizzes**: Quiz system with auto-grading and instructor feedback
- **dashboard**: Personalized dashboards and analytics

### Key Technologies:
- **Backend**: Django 4.x, Django REST Framework, PostgreSQL
- **Frontend**: Django Templates with Bootstrap 5, responsive design
- **Storage**: AWS S3 for media files, WhiteNoise for static files
- **Authentication**: Django Auth + JWT for API access
- **Deployment**: Docker, AWS Elastic Beanstalk, Gunicorn

## Development Guidelines

### Models:
- Use custom User model with role-based permissions
- Implement proper relationships between courses, enrollments, and progress tracking
- Include comprehensive metadata fields for analytics

### Views:
- Use class-based views for consistency
- Implement proper permission checks based on user roles
- Include pagination for list views

### Templates:
- Extend base.html for consistent layout
- Use Bootstrap 5 components and utilities
- Implement responsive design patterns

### API:
- Use Django REST Framework for API endpoints
- Implement JWT authentication for mobile/frontend apps
- Follow RESTful conventions

### Security:
- Never hardcode secrets (use environment variables)
- Implement proper CSRF protection
- Use HTTPS in production
- Validate user permissions for all operations

### AWS Deployment:
- Use environment variables for configuration
- Implement health checks
- Configure auto-scaling and load balancing
- Use S3 for media storage with proper permissions

## Code Style:
- Follow Django best practices
- Use descriptive variable and function names
- Include docstrings for complex methods
- Implement proper error handling
- Use Django's built-in features when possible
