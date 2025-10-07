# Monitoring & Observability Guide

This guide covers monitoring, logging, and observability practices for the Django LMS application in production.

## 📊 Monitoring Strategy

### Key Metrics to Monitor

#### Application Metrics
- **Response Time**: Average, p95, p99 response times
- **Request Rate**: Requests per second/minute
- **Error Rate**: 4xx and 5xx errors
- **Throughput**: Successful requests per time period
- **Active Users**: Current active sessions

#### Infrastructure Metrics
- **CPU Usage**: Application server CPU utilization
- **Memory Usage**: Application server memory usage
- **Disk I/O**: Read/write operations
- **Network I/O**: Inbound/outbound traffic

#### Database Metrics
- **Connection Pool**: Active/idle connections
- **Query Performance**: Slow query log
- **Database Size**: Growth over time
- **Replication Lag**: For read replicas

#### Business Metrics
- **User Registrations**: New users per day/week
- **Course Enrollments**: Active enrollments
- **Quiz Completions**: Completion rates
- **Active Courses**: Courses with activity

## 🔍 Application Monitoring

### Health Check Endpoint

The application includes a `/health/` endpoint that checks:
- Application responsiveness
- Database connectivity
- Cache availability (if Redis enabled)

```bash
# Check application health
curl https://your-domain.com/health/

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "ok",
  "cache": "ok"
}
```

### Django Admin Monitoring

Access Django admin to monitor:
- Recent user activity
- System logs
- Failed login attempts
- Content creation/updates

## 📝 Logging

### Log Levels

The application uses the following log levels:
- **DEBUG**: Detailed information for diagnosing problems (development only)
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical messages for very serious errors

### Log Files

#### Local Development
- `django.log`: General application logs
- `django_errors.log`: Error-level logs only

#### Production (AWS CloudWatch)
Logs are sent to CloudWatch Logs with the following groups:
- `/aws/elasticbeanstalk/django-lms/application`
- `/aws/elasticbeanstalk/django-lms/errors`

### Application Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log examples
logger.info('User enrolled in course', extra={
    'user_id': user.id,
    'course_id': course.id
})

logger.error('Payment processing failed', extra={
    'user_id': user.id,
    'error': str(e)
})
```

### Structured Logging

For better log analysis, use structured logging:

```python
logger.info('course_enrollment', extra={
    'event_type': 'enrollment',
    'user_id': user.id,
    'course_id': course.id,
    'timestamp': timezone.now().isoformat()
})
```

## 🚨 Error Tracking

### Sentry Integration

Configure Sentry for error tracking:

```env
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
ENVIRONMENT=production
```

Sentry automatically captures:
- Unhandled exceptions
- HTTP errors (4xx, 5xx)
- Database errors
- Custom events

### Custom Error Tracking

```python
from sentry_sdk import capture_exception, capture_message

try:
    # Your code
    pass
except Exception as e:
    capture_exception(e)
    logger.error(f'Custom error: {e}')
```

## 📈 AWS CloudWatch

### CloudWatch Metrics

#### Default Metrics (Elastic Beanstalk)
- Environment health
- Instance health
- Application requests
- HTTP response codes
- Latency

#### Custom Metrics

Create custom metrics for business events:

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def track_enrollment(user_id, course_id):
    cloudwatch.put_metric_data(
        Namespace='LMS/Business',
        MetricData=[
            {
                'MetricName': 'CourseEnrollments',
                'Value': 1,
                'Unit': 'Count'
            }
        ]
    )
```

### CloudWatch Alarms

Recommended alarms:

#### Application Alarms
1. **High Error Rate**
   - Metric: HTTP 5xx errors
   - Threshold: > 5% of requests
   - Period: 5 minutes

2. **Slow Response Time**
   - Metric: Latency p99
   - Threshold: > 3 seconds
   - Period: 5 minutes

3. **Application Unhealthy**
   - Metric: Health check failures
   - Threshold: > 2 consecutive failures
   - Period: 1 minute

#### Infrastructure Alarms
1. **High CPU Usage**
   - Metric: CPU Utilization
   - Threshold: > 80%
   - Period: 5 minutes

2. **High Memory Usage**
   - Metric: Memory Utilization
   - Threshold: > 85%
   - Period: 5 minutes

3. **Disk Space**
   - Metric: Disk Space Utilization
   - Threshold: > 80%
   - Period: 5 minutes

#### Database Alarms
1. **High Database Connections**
   - Metric: DatabaseConnections
   - Threshold: > 80% of max
   - Period: 5 minutes

2. **Slow Queries**
   - Metric: ReadLatency/WriteLatency
   - Threshold: > 100ms
   - Period: 5 minutes

## 🔔 Alerting

### Notification Channels

Configure AWS SNS topics for:
- **Critical**: Immediate attention required (SMS + Email)
- **Warning**: Attention needed soon (Email)
- **Info**: Informational notifications (Email)

### Alert Response

#### Critical Alerts
1. Acknowledge the alert
2. Check application health dashboard
3. Review recent deployments
4. Check error logs
5. Execute runbook procedures
6. Escalate if needed

#### Warning Alerts
1. Review metrics trends
2. Check for resource constraints
3. Plan capacity adjustments
4. Document findings

## 📊 Dashboards

### CloudWatch Dashboard

Create a custom dashboard with:

#### Overview Panel
- Application health status
- Request rate (last hour)
- Error rate (last hour)
- Average latency

#### Performance Panel
- Response time (p50, p95, p99)
- Request throughput
- Database query time
- Cache hit rate

#### Infrastructure Panel
- CPU utilization
- Memory utilization
- Network I/O
- Disk I/O

#### Business Panel
- Active users
- New registrations (daily)
- Course enrollments (daily)
- Quiz completions (daily)

### Third-Party Monitoring

Consider integrating:
- **Datadog**: Application performance monitoring
- **New Relic**: Full-stack observability
- **Prometheus + Grafana**: Open-source monitoring
- **UptimeRobot**: Uptime monitoring

## 🔧 Performance Monitoring

### Django Debug Toolbar (Development Only)

Never enable in production! Use for local development:

```python
# settings.py (development only)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### SQL Query Analysis

Monitor slow queries:

```python
# settings.py
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',  # Only in staging for analysis
            'handlers': ['console'],
        }
    }
}
```

### Performance Profiling

Use Django Silk or django-cprofile for profiling:

```bash
pip install django-silk

# Add to INSTALLED_APPS
INSTALLED_APPS += ['silk']

# Add to MIDDLEWARE
MIDDLEWARE += ['silk.middleware.SilkyMiddleware']
```

## 📱 Uptime Monitoring

### External Monitoring

Configure external monitoring with:
- **Pingdom**: Every 1 minute checks
- **UptimeRobot**: Free 5-minute checks
- **StatusCake**: Multiple location checks

### Endpoints to Monitor

1. **Homepage**: `https://your-domain.com/`
2. **Health Check**: `https://your-domain.com/health/`
3. **API Health**: `https://your-domain.com/api/health/`
4. **Login Page**: `https://your-domain.com/users/login/`

## 🎯 Key Performance Indicators (KPIs)

### Technical KPIs
- **Uptime**: Target 99.9% (< 43 minutes downtime/month)
- **Response Time**: p95 < 500ms
- **Error Rate**: < 0.1%
- **Availability**: 99.9%

### Business KPIs
- **Daily Active Users (DAU)**
- **Monthly Active Users (MAU)**
- **Course Completion Rate**
- **User Engagement Score**

## 🔄 Regular Maintenance

### Daily Tasks
- Review error logs
- Check system health dashboard
- Monitor alert notifications
- Review user feedback

### Weekly Tasks
- Analyze performance trends
- Review slow queries
- Check disk usage
- Update monitoring thresholds

### Monthly Tasks
- Generate performance reports
- Review and update alerts
- Capacity planning review
- Security audit logs review

## 📚 Resources

### AWS CloudWatch
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [Elastic Beanstalk Monitoring](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/health-enhanced.html)

### Django
- [Django Logging](https://docs.djangoproject.com/en/4.2/topics/logging/)
- [Django Performance](https://docs.djangoproject.com/en/4.2/topics/performance/)

### Sentry
- [Sentry Django Guide](https://docs.sentry.io/platforms/python/guides/django/)

---

**Remember**: Good monitoring is proactive, not reactive!
