# Generated by Django 4.2.7 on 2025-07-05 17:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('login', 'Logged in'), ('logout', 'Logged out'), ('course_enrolled', 'Enrolled in course'), ('course_completed', 'Completed course'), ('lesson_completed', 'Completed lesson'), ('quiz_attempted', 'Attempted quiz'), ('quiz_passed', 'Passed quiz'), ('certificate_earned', 'Earned certificate'), ('profile_updated', 'Updated profile'), ('course_created', 'Created course'), ('course_updated', 'Updated course'), ('lesson_created', 'Created lesson'), ('student_graded', 'Graded student')], max_length=50)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('announcement_type', models.CharField(choices=[('system', 'System-wide'), ('course', 'Course-specific'), ('maintenance', 'Maintenance'), ('feature', 'New Feature'), ('policy', 'Policy Update')], default='system', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20)),
                ('target_user_types', models.CharField(default='student,instructor,admin', help_text='Comma-separated list of user types (student, instructor, admin)', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('published_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('is_dismissible', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-published_at'],
            },
        ),
        migrations.CreateModel(
            name='AnnouncementView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('is_dismissed', models.BooleanField(default=False)),
                ('dismissed_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DashboardSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_progress_charts', models.BooleanField(default=True)),
                ('show_recent_activity', models.BooleanField(default=True)),
                ('show_upcoming_deadlines', models.BooleanField(default=True)),
                ('show_course_recommendations', models.BooleanField(default=True)),
                ('email_notifications', models.BooleanField(default=True)),
                ('push_notifications', models.BooleanField(default=True)),
                ('weekly_progress_email', models.BooleanField(default=True)),
                ('theme', models.CharField(choices=[('light', 'Light'), ('dark', 'Dark'), ('auto', 'Auto')], default='light', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LearningPath',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
                ('estimated_duration_weeks', models.PositiveIntegerField(help_text='Estimated weeks to complete')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LearningPathCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_required', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='StudyGoal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('goal_type', models.CharField(choices=[('daily_minutes', 'Daily Study Time'), ('weekly_lessons', 'Weekly Lessons'), ('monthly_courses', 'Monthly Course Completion'), ('custom', 'Custom Goal')], max_length=20)),
                ('target_value', models.PositiveIntegerField(help_text='Target number (minutes, lessons, courses, etc.)')),
                ('current_value', models.PositiveIntegerField(default=0)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
