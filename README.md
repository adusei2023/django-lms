# LMS - Learning Management System

A comprehensive Learning Management System built with Django 4.x, designed for scalable deployment on AWS Elastic Beanstalk.

## 🎓 Features

### 👤 User Management
- **Custom User Model** with role-based access (Student, Instructor, Admin)
- **Authentication System** with login, registration, password reset, and email verification
- **User Profiles** with avatars, bio, and extended information
- **Role-specific Dashboards** for different user types

### 📚 Course Management
- **Course Creation** with rich content support
- **Modular Structure** with courses divided into modules and lessons
- **Multiple Content Types** - videos, PDFs, articles, quizzes
- **SEO-friendly URLs** with slug-based routing
- **Course Reviews** and rating system
- **Resource Management** for additional course materials

### 📝 Enrollment & Progress Tracking
- **Easy Enrollment** for free and paid courses
- **Progress Tracking** with completion percentages
- **Lesson Completion** tracking with bookmarks and notes
- **Certificate Generation** upon course completion
- **Learning Analytics** for students and instructors

### ❓ Quiz System
- **Multiple Question Types** - Multiple choice, True/False, Short answer, Essay
- **Auto-grading** with instant feedback
- **Timed Quizzes** with customizable time limits
- **Multiple Attempts** with attempt tracking
- **Instructor Feedback** and manual grading for essay questions

### 📊 Dashboard & Analytics
- **Personalized Dashboards** for all user types
- **Study Goals** and progress tracking
- **Learning Paths** for structured learning
- **Activity Logs** and engagement tracking
- **Announcements** system for important updates

## 🛠 Technical Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Primary database
- **Redis** - Caching and sessions (optional)
- **Celery** - Background tasks (optional)

### Frontend
- **Django Templates** - Server-side rendering
- **Bootstrap 5** - UI framework
- **Font Awesome** - Icons
- **Custom CSS** - Enhanced styling

### Storage & Media
- **AWS S3** - Media file storage (production)
- **WhiteNoise** - Static file serving
- **Pillow** - Image processing

### Deployment
- **Docker** - Containerization
- **AWS Elastic Beanstalk** - Platform deployment
- **Gunicorn** - WSGI server
- **Nginx** - Reverse proxy

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (for production)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lms-django
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py create_superuser_if_none_exists
   python manage.py create_sample_data  # Optional: Load sample data
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**
   - Web App: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin
   - API: http://localhost:8000/api

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations in container**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py create_superuser_if_none_exists
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/lms_db

# AWS S3 (Production)
USE_S3=False
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
```

## ☁️ AWS Deployment

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- EB CLI installed

### Deployment Steps

1. **Prepare for deployment**
   ```bash
   # Update environment variables for production
   # Set DEBUG=False in production environment
   ```

2. **Initialize Elastic Beanstalk**
   ```bash
   eb init
   ```

3. **Create environment**
   ```bash
   eb create lms-production
   ```

4. **Set environment variables**
   ```bash
   eb setenv DEBUG=False
   eb setenv SECRET_KEY=your-production-secret-key
   eb setenv DATABASE_URL=your-rds-database-url
   eb setenv USE_S3=True
   eb setenv AWS_STORAGE_BUCKET_NAME=your-s3-bucket
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

### AWS Services Required

- **Elastic Beanstalk** - Application hosting
- **RDS PostgreSQL** - Database
- **S3** - Media file storage
- **CloudFront** - CDN (optional)
- **SES** - Email service
- **Route 53** - DNS management
- **ACM** - SSL certificates

## 📱 API Documentation

The application includes a REST API built with Django REST Framework:

- **Authentication**: JWT tokens
- **Endpoints**: `/api/` prefix
- **Documentation**: Available at `/api/docs/` (when configured)

### Key API Endpoints

```
POST /api/auth/token/          # Get JWT token
POST /api/auth/token/refresh/  # Refresh JWT token
GET  /api/courses/            # List courses
GET  /api/courses/{id}/       # Course details
POST /api/enrollments/        # Enroll in course
GET  /api/quizzes/            # List quizzes
POST /api/quizzes/{id}/start/ # Start quiz attempt
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test courses

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📁 Project Structure

```
lms-django/
├── lms_project/           # Django project settings
├── users/                 # User management app
├── courses/              # Course management app
├── enrollments/          # Enrollment tracking app
├── quizzes/              # Quiz system app
├── dashboard/            # Dashboard and analytics app
├── api/                  # API configuration
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploaded files
├── .ebextensions/        # AWS Elastic Beanstalk config
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Multi-container setup
└── README.md           # This file
```

## 🔐 Security Features

- **CSRF Protection** - Built-in Django CSRF protection
- **SQL Injection Prevention** - Django ORM protection
- **XSS Protection** - Template auto-escaping
- **Secure Headers** - Security middleware configured
- **Password Validation** - Strong password requirements
- **Email Verification** - Account security
- **Permission System** - Role-based access control

## 📈 Performance Optimizations

- **Database Indexing** - Optimized database queries
- **Caching** - Redis support for session and cache
- **Static File Optimization** - WhiteNoise for static files
- **Image Optimization** - Automatic image resizing
- **Lazy Loading** - Efficient data loading
- **CDN Integration** - AWS CloudFront support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and code comments
- **Issues**: Report bugs via GitHub Issues
- **Email**: Contact the development team

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core LMS functionality
- ✅ User management
- ✅ Course creation and management
- ✅ Quiz system
- ✅ AWS deployment ready

### Phase 2 (Future)
- 📱 Mobile app (React Native)
- 💬 Discussion forums
- 📹 Live streaming integration
- 💳 Payment gateway integration
- 📊 Advanced analytics
- 🤖 AI-powered recommendations

### Phase 3 (Advanced)
- 🌍 Multi-language support
- 📱 Progressive Web App (PWA)
- 🔄 Real-time collaboration
- 📈 Advanced reporting
- 🎯 Gamification features

---

**Happy Learning! 🎓**
