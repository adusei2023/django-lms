"""
Management command to backup the database.
Creates a JSON dump of all data excluding sensitive content types.
"""
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Create a database backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Directory to store backups (default: backups/)'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='json',
            choices=['json', 'xml'],
            help='Format for the backup (default: json)'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        backup_format = options['format']

        # Create backup directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.stdout.write(self.style.SUCCESS(f'Created backup directory: {output_dir}'))

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(output_dir, f'backup_{timestamp}.{backup_format}')

        try:
            self.stdout.write('Creating database backup...')
            
            # Create backup excluding sensitive data
            with open(filename, 'w') as f:
                call_command(
                    'dumpdata',
                    '--natural-foreign',
                    '--natural-primary',
                    '--exclude', 'contenttypes',
                    '--exclude', 'auth.Permission',
                    '--exclude', 'sessions.Session',
                    '--format', backup_format,
                    stdout=f
                )

            # Check file size
            file_size = os.path.getsize(filename)
            size_mb = file_size / (1024 * 1024)

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Backup created successfully: {filename} ({size_mb:.2f} MB)'
                )
            )

            # Cleanup old backups (keep last 10)
            self.cleanup_old_backups(output_dir, keep=10)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Backup failed: {str(e)}')
            )
            if os.path.exists(filename):
                os.remove(filename)
            raise

    def cleanup_old_backups(self, output_dir, keep=10):
        """Remove old backups keeping only the most recent ones"""
        backup_files = []
        for filename in os.listdir(output_dir):
            if filename.startswith('backup_') and (filename.endswith('.json') or filename.endswith('.xml')):
                filepath = os.path.join(output_dir, filename)
                backup_files.append((filepath, os.path.getmtime(filepath)))

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x[1], reverse=True)

        # Remove old backups
        removed_count = 0
        for filepath, _ in backup_files[keep:]:
            try:
                os.remove(filepath)
                removed_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Could not remove old backup {filepath}: {str(e)}')
                )

        if removed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Cleaned up {removed_count} old backup(s)')
            )
