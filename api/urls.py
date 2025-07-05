from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .viewsets import (
    UserViewSet, UserProfileViewSet, CategoryViewSet,
    CourseViewSet, EnrollmentViewSet, QuizViewSet, QuizAttemptViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quizattempt')
urlpatterns = [
    # DRF router URLs
    path('', include(router.urls)),
    
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # DRF Browsable API auth
    path('auth/', include('rest_framework.urls')),
]
