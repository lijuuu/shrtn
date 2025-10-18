"""
Test command for ScyllaDB implementation using repository pattern.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.dependencies.database import db_dependency
from urls.repositories import UrlRepository
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test ScyllaDB implementation for URL shortening using repository pattern'

    def add_arguments(self, parser):
        parser.add_argument(
            '--namespace-id',
            type=int,
            default=1,
            help='Namespace ID for testing (default: 1)'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=1,
            help='User ID for testing (default: 1)'
        )

    def handle(self, *args, **options):
        namespace_id = options['namespace_id']
        user_id = options['user_id']
        
        self.stdout.write(
            self.style.SUCCESS(f'Testing ScyllaDB with namespace_id={namespace_id}, user_id={user_id}')
        )
        
        try:
            # Initialize repository
            scylla_connection = db_dependency.get_scylla()
            url_repository = UrlRepository(scylla_connection)
            
            # Test 1: Create a short URL
            self.stdout.write('Test 1: Creating short URL...')
            url_data = {
                'namespace_id': namespace_id,
                'shortcode': 'test123',
                'original_url': 'https://example.com/test',
                'created_by_user_id': user_id,
                'is_private': False,
                'tags': ['test', 'demo']
            }
            short_url = url_repository.create(url_data)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created short URL: {short_url.shortcode} -> {short_url.original_url}')
            )
            
            # Test 2: Get the short URL
            self.stdout.write('Test 2: Retrieving short URL...')
            retrieved_url = url_repository.get_by_id((namespace_id, 'test123'))
            if retrieved_url:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Retrieved: {retrieved_url.shortcode} -> {retrieved_url.original_url}')
                )
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to retrieve short URL'))
            
            # Test 3: Increment click count
            self.stdout.write('Test 3: Incrementing click count...')
            success = url_repository.increment_click_count(namespace_id, 'test123')
            if success:
                self.stdout.write(self.style.SUCCESS('✓ Click count incremented'))
                
                # Verify click count
                updated_url = url_repository.get_by_id((namespace_id, 'test123'))
                if updated_url:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Click count is now: {updated_url.click_count}')
                    )
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to increment click count'))
            
            # Test 4: Get URLs by user
            self.stdout.write('Test 4: Getting URLs by user...')
            user_urls = url_repository.list({'created_by_user_id': user_id})
            self.stdout.write(
                self.style.SUCCESS(f'✓ Found {len(user_urls)} URLs for user {user_id}')
            )
            
            # Test 5: Batch create URLs
            self.stdout.write('Test 5: Batch creating URLs...')
            batch_data = [
                {
                    'namespace_id': namespace_id,
                    'shortcode': 'batch1',
                    'original_url': 'https://example.com/batch1',
                    'created_by_user_id': user_id,
                    'is_private': False,
                    'tags': ['batch', 'test']
                },
                {
                    'namespace_id': namespace_id,
                    'shortcode': 'batch2',
                    'original_url': 'https://example.com/batch2',
                    'created_by_user_id': user_id,
                    'is_private': True,
                    'tags': ['batch', 'private']
                }
            ]
            batch_results = url_repository.batch_create(batch_data)
            self.stdout.write(
                self.style.SUCCESS(f'✓ Batch created {len(batch_results)} URLs')
            )
            
            # Test 6: Delete a URL
            self.stdout.write('Test 6: Deleting short URL...')
            delete_success = url_repository.delete((namespace_id, 'test123'))
            if delete_success:
                self.stdout.write(self.style.SUCCESS('✓ Short URL deleted'))
                
                # Verify deletion
                deleted_url = url_repository.get_by_id((namespace_id, 'test123'))
                if not deleted_url:
                    self.stdout.write(self.style.SUCCESS('✓ Deletion verified'))
                else:
                    self.stdout.write(self.style.ERROR('✗ URL still exists after deletion'))
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to delete short URL'))
            
            self.stdout.write(
                self.style.SUCCESS('\n🎉 All ScyllaDB tests completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Test failed with error: {e}')
            )
            logger.exception("ScyllaDB test failed")
            raise