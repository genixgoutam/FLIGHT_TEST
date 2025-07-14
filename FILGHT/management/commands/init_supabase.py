from django.core.management.base import BaseCommand
from django.conf import settings
from FILGHT.supabase_utils import initialize_supabase_report_data, test_supabase_connection


class Command(BaseCommand):
    help = 'Initialize Supabase with sample report data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Only test the Supabase connection without initializing data',
        )

    def handle(self, *args, **options):
        if options['test_only']:
            self.stdout.write('Testing Supabase connection...')
            if test_supabase_connection():
                self.stdout.write(
                    self.style.SUCCESS('✓ Supabase connection successful!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Supabase connection failed!')
                )
            return

        self.stdout.write('Initializing Supabase with sample report data...')
        
        # Test connection first
        if not test_supabase_connection():
            self.stdout.write(
                self.style.ERROR('✗ Supabase connection failed! Please check your credentials.')
            )
            return

        # Initialize data
        if initialize_supabase_report_data():
            self.stdout.write(
                self.style.SUCCESS('✓ Successfully initialized Supabase with sample report data!')
            )
            self.stdout.write('You can now view the report at /report/')
        else:
            self.stdout.write(
                self.style.ERROR('✗ Failed to initialize Supabase data!')
            ) 