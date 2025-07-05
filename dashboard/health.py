from django.http import JsonResponse
from django.views import View
from django.db import connection


class HealthCheckView(View):
    """Health check endpoint for AWS Elastic Beanstalk"""
    
    def get(self, request):
        try:
            # Check database connectivity
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            return JsonResponse({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': '2025-01-05T12:00:00Z'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': '2025-01-05T12:00:00Z'
            }, status=503)
