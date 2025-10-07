# Quick Reference - Production Operations

A quick reference guide for common production operations and commands.

## 🚨 Emergency Response

### Application Down
```bash
# Check health
curl https://your-domain.com/health/

# Check logs
tail -100 django_errors.log

# Check AWS EB health
aws elasticbeanstalk describe-environment-health --environment-name django-lms-prod
```

### High Error Rate
```bash
# View recent errors
tail -100 django_errors.log | grep ERROR

# Check Sentry dashboard
# Visit: https://sentry.io

# Check CloudWatch alarms
# AWS Console → CloudWatch → Alarms
```

### Database Issues
```bash
# Check database connectivity
python manage.py dbshell

# Check active connections
SELECT count(*) FROM pg_stat_activity;

# Check long-running queries
SELECT pid, now() - query_start as duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC;
```

## 📊 Daily Operations

### Check Application Status
```bash
# Health check
curl https://your-domain.com/health/

# Check deployment status
make deploy-check

# View recent logs
tail -50 django.log
```

### Monitor Performance
```bash
# Check CloudWatch metrics
# AWS Console → CloudWatch → Dashboards

# Review Sentry issues
# https://sentry.io

# Check Redis status
redis-cli -h your-redis-host info stats
```

## 🔧 Maintenance Operations

### Database Backup
```bash
# Create backup
python manage.py backup_database

# Create backup with custom location
python manage.py backup_database --output-dir=/backups

# Check existing backups
ls -lh backups/
```

### Database Migrations
```bash
# Show migration status
python manage.py showmigrations

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Rollback migration (if needed)
python manage.py migrate app_name previous_migration_name
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Clear old static files
python manage.py collectstatic --noinput --clear
```

### Cache Management
```bash
# Clear all cache
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Check Redis memory usage
redis-cli -h your-redis-host info memory

# Flush Redis cache
redis-cli -h your-redis-host FLUSHDB
```

## 🧪 Testing & Validation

### Run Tests
```bash
# All tests
make test

# Specific app
python manage.py test users

# With coverage
make coverage

# Fast tests (exclude slow)
pytest -m "not slow"
```

### Code Quality
```bash
# Run all quality checks
make lint

# Format code
make format

# Security scan
bandit -r . -x ./venv,./tests

# Check dependencies
safety check
```

### Deployment Checks
```bash
# Django deployment check
python manage.py check --deploy

# Full check with Make
make deploy-check
```

## 📈 Monitoring Commands

### View Logs
```bash
# Application logs (last 100 lines)
tail -100 django.log

# Error logs only
tail -100 django_errors.log

# Follow logs in real-time
tail -f django.log

# Search for specific errors
grep "ERROR" django.log | tail -20

# Search with context
grep -A 5 -B 5 "ERROR" django.log
```

### Database Performance
```bash
# Check slow queries
python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)

# Database size
SELECT pg_size_pretty(pg_database_size('lms_db'));

# Table sizes
SELECT schemaname, tablename, 
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 🔐 Security Operations

### User Management
```bash
# Create superuser
python manage.py createsuperuser

# Create superuser if none exists
python manage.py create_superuser_if_none_exists

# Change user password
python manage.py changepassword username
```

### Security Audit
```bash
# Django security check
python manage.py check --deploy

# Scan for security issues
bandit -r . -f json -o security_report.json

# Check dependency vulnerabilities
safety check --json
```

## 🐳 Docker Operations

### Container Management
```bash
# Start containers
make docker-up

# Stop containers
make docker-down

# Restart containers
docker-compose restart

# View logs
make docker-logs

# Execute commands in container
docker-compose exec web python manage.py shell
```

### Container Debugging
```bash
# Access container shell
docker-compose exec web bash

# Check container resources
docker stats

# View container processes
docker-compose top
```

## 📦 Deployment Operations

### Deploy to AWS EB
```bash
# Deploy current version
eb deploy

# Deploy with custom label
eb deploy --label v1.2.3

# Check deployment status
eb status

# View recent events
eb events --follow
```

### Environment Configuration
```bash
# List environment variables
eb printenv

# Set environment variable
eb setenv DEBUG=False

# Set multiple variables
eb setenv VAR1=value1 VAR2=value2
```

## 🔄 Rollback Procedures

### Application Rollback
```bash
# List previous versions
eb appversion

# Deploy previous version
eb deploy --version previous_version_label

# Swap environments (Blue/Green)
eb swap django-lms-prod --destination-name django-lms-staging
```

### Database Rollback
```bash
# Rollback migration
python manage.py migrate app_name previous_migration

# Restore from backup
python manage.py loaddata backups/backup_20240115_120000.json
```

## 📊 Performance Tuning

### Identify Slow Queries
```bash
# Enable query logging temporarily
# Add to settings.py:
LOGGING['loggers']['django.db.backends'] = {
    'level': 'DEBUG',
    'handlers': ['console'],
}

# Or use django-debug-toolbar in staging
```

### Cache Optimization
```bash
# Check cache hit rate
redis-cli -h your-redis-host info stats

# Monitor cache keys
redis-cli -h your-redis-host keys "lms:*" | wc -l

# Clear specific cache keys
redis-cli -h your-redis-host keys "lms:specific_pattern*" | xargs redis-cli DEL
```

## 📝 Useful SQL Queries

### User Statistics
```sql
-- Active users today
SELECT COUNT(*) FROM users_user WHERE last_login >= CURRENT_DATE;

-- New registrations this week
SELECT COUNT(*) FROM users_user WHERE date_joined >= CURRENT_DATE - INTERVAL '7 days';

-- Users by role
SELECT role, COUNT(*) FROM users_user GROUP BY role;
```

### Course Statistics
```sql
-- Total enrollments
SELECT COUNT(*) FROM enrollments_enrollment;

-- Enrollments this month
SELECT COUNT(*) FROM enrollments_enrollment 
WHERE enrolled_at >= DATE_TRUNC('month', CURRENT_DATE);

-- Top courses by enrollment
SELECT c.title, COUNT(e.id) as enrollment_count
FROM courses_course c
LEFT JOIN enrollments_enrollment e ON c.id = e.course_id
GROUP BY c.id, c.title
ORDER BY enrollment_count DESC
LIMIT 10;
```

## 🔔 Alert Response

### High CPU Usage
1. Check CloudWatch metrics
2. Review slow queries
3. Check for runaway processes
4. Consider scaling up
5. Review recent deployments

### High Memory Usage
1. Check for memory leaks
2. Review cache size
3. Check query performance
4. Consider increasing instance size
5. Review application code

### Disk Space Low
1. Clear old log files: `make clean`
2. Remove old backups
3. Check media file growth
4. Consider S3 migration
5. Increase disk size

## 📞 Escalation

### Critical Issues (P1)
- Application completely down
- Data loss risk
- Security breach
- Contact: on-call engineer immediately

### High Priority (P2)
- Partial outage
- Major feature broken
- High error rate
- Contact: on-call engineer within 1 hour

### Medium Priority (P3)
- Minor feature issues
- Performance degradation
- Contact: team during business hours

---

## 📚 Additional Resources

- **Full Checklist**: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
- **Monitoring Guide**: [MONITORING.md](MONITORING.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Feature Summary**: [PRODUCTION_FEATURES.md](PRODUCTION_FEATURES.md)

---

**Keep this guide handy for quick reference during incidents!**
