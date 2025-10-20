"""
Django management command to create analytics table in ScyllaDB.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create analytics table in ScyllaDB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if table exists',
        )

    def handle(self, *args, **options):
        try:
            from core.dependencies.service_registry import service_registry
            
            # Get ScyllaDB connection
            scylla = service_registry.get_scylla()
            if not scylla:
                raise CommandError('ScyllaDB connection not available')
            
            if not scylla.is_connected():
                self.stdout.write('Connecting to ScyllaDB...')
                scylla.connect()
            
            # Read schema from file
            schema_file = 'analytics/schema.cql'
            try:
                with open(schema_file, 'r') as f:
                    schema = f.read()
            except FileNotFoundError:
                raise CommandError(f'Schema file not found: {schema_file}')
            
            # Split schema into individual statements
            statements = [stmt.strip() for stmt in schema.split(';') if stmt.strip()]
            
            self.stdout.write('Creating analytics table...')
            
            for statement in statements:
                if statement:
                    try:
                        self.stdout.write(f'Executing: {statement[:50]}...')
                        scylla.execute_query(statement)
                        self.stdout.write(self.style.SUCCESS('✓ Table created successfully'))
                    except Exception as e:
                        if 'already exists' in str(e).lower() and not options['force']:
                            self.stdout.write(self.style.WARNING(f'⚠ Table already exists: {e}'))
                        else:
                            raise CommandError(f'Failed to create table: {e}')
            
            self.stdout.write(
                self.style.SUCCESS('Analytics table created successfully!')
            )
            
        except Exception as e:
            raise CommandError(f'Failed to create analytics table: {e}')
