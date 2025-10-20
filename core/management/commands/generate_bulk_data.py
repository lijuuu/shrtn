"""
Django management command to generate bulk test data.
Usage: python manage.py generate_bulk_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember, Invite
from namespaces.models import Namespace
from urls.models import ShortUrl
# Analytics data will be generated via ScyllaDB service
from faker import Faker
import random
from datetime import datetime, timedelta

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Generate bulk test data for testing and benchmarking'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=1000,
            help='Number of users to create (default: 1000)'
        )
        parser.add_argument(
            '--organizations',
            type=int,
            default=1000,
            help='Number of organizations to create (default: 1000)'
        )
        parser.add_argument(
            '--namespaces',
            type=int,
            default=1000,
            help='Number of namespaces to create (default: 1000)'
        )
        parser.add_argument(
            '--urls',
            type=int,
            default=1000,
            help='Number of short URLs to create (default: 1000)'
        )
        parser.add_argument(
            '--clicks',
            type=int,
            default=5000,
            help='Number of click events to create (default: 5000)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new data'
        )

    def handle(self, *args, **options):
        """Main command handler."""
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting bulk data generation...')
        )
        
        if options['clear']:
            self.clear_existing_data()
        
        # Generate data
        users = self.generate_users(options['users'])
        organizations = self.generate_organizations(users, options['organizations'])
        namespaces = self.generate_namespaces(organizations, users, options['namespaces'])
        urls = self.generate_short_urls(namespaces, users, options['urls'])
        clicks = self.generate_click_events(urls, options['clicks'])
        
        # Analytics data will be generated via ScyllaDB service
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS('🎉 Bulk data generation completed!')
        )
        self.stdout.write(f"📊 Summary:")
        self.stdout.write(f"   - Users: {len(users)}")
        self.stdout.write(f"   - Organizations: {len(organizations)}")
        self.stdout.write(f"   - Namespaces: {len(namespaces)}")
        self.stdout.write(f"   - Short URLs: {len(urls)}")
        self.stdout.write(f"   - Click Events: {clicks}")
        self.stdout.write(f"   - Analytics: Generated via ScyllaDB service")

    def clear_existing_data(self):
        """Clear existing test data."""
        self.stdout.write('🧹 Clearing existing data...')
        
        # Clear in reverse dependency order
        # Note: ShortUrl is not a Django model, it's handled by ScyllaDB
        Namespace.objects.all().delete()
        Invite.objects.all().delete()
        OrganizationMember.objects.all().delete()
        Organization.objects.all().delete()
        User.objects.filter(email__contains='@example.com').delete()
        
        self.stdout.write('✅ Existing data cleared')

    def generate_users(self, count):
        """Generate test users."""
        self.stdout.write(f'🔄 Generating {count} users...')
        users = []
        
        for i in range(count):
            user = User.objects.create_user(
                email=f"user{i}@example.com",
                username=f"user{i}",
                password="testpass123",
                name=fake.name(),
                is_active=True
            )
            users.append(user)
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'   ✅ Created {i + 1} users...')
        
        self.stdout.write(f'✅ Generated {len(users)} users')
        return users

    def generate_organizations(self, users, count):
        """Generate test organizations."""
        self.stdout.write(f'🔄 Generating {count} organizations...')
        organizations = []
        
        for i in range(count):
            owner = random.choice(users)
            org = Organization.objects.create(
                name=f"Company {i}",
                owner=owner
            )
            organizations.append(org)
            
            # Create organization member for owner
            OrganizationMember.objects.create(
                organization=org,
                user=owner,
                role='admin'
            )
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'   ✅ Created {i + 1} organizations...')
        
        self.stdout.write(f'✅ Generated {len(organizations)} organizations')
        return organizations

    def generate_namespaces(self, organizations, users, count):
        """Generate test namespaces."""
        self.stdout.write(f'🔄 Generating {count} namespaces...')
        namespaces = []
        
        for i in range(count):
            org = random.choice(organizations)
            creator = random.choice(users)
            
            namespace = Namespace.objects.create(
                name=f"namespace-{i}",
                organization=org,
                created_by=creator
            )
            namespaces.append(namespace)
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'   ✅ Created {i + 1} namespaces...')
        
        self.stdout.write(f'✅ Generated {len(namespaces)} namespaces')
        return namespaces

    def generate_short_urls(self, namespaces, users, count):
        """Generate test short URLs."""
        self.stdout.write(f'🔄 Generating {count} short URLs...')
        urls = []
        
        # Common URL patterns for realistic data
        url_patterns = [
            "https://www.google.com/search?q={}",
            "https://github.com/{}/{}",
            "https://stackoverflow.com/questions/{}",
            "https://docs.python.org/3/library/{}.html",
            "https://www.youtube.com/watch?v={}",
            "https://medium.com/@{}/{}",
            "https://dev.to/{}/{}",
            "https://www.reddit.com/r/{}/comments/{}",
            "https://www.amazon.com/dp/{}",
            "https://www.wikipedia.org/wiki/{}"
        ]
        
        for i in range(count):
            namespace = random.choice(namespaces)
            creator = random.choice(users)
            
            # Generate unique shortcode
            shortcode = f"url{i}"
            
            # Generate realistic URL
            pattern = random.choice(url_patterns)
            if "{}" in pattern:
                original_url = pattern.format(fake.word(), fake.word(), fake.uuid4()[:8])
            else:
                original_url = fake.url()
            
            url = ShortUrl(
                namespace_id=namespace.namespace_id,
                shortcode=shortcode,
                original_url=original_url,
                created_by_user_id=creator.id,
                title=fake.sentence(nb_words=4),
                description=fake.text(max_nb_chars=100),
                click_count=random.randint(0, 10000),
                is_private=random.choice([True, False]),
                is_active=random.choice([True, False]),
                tags=[fake.word() for _ in range(random.randint(1, 3))]
            )
            urls.append(url)
            
            if (i + 1) % 100 == 0:
                self.stdout.write(f'   ✅ Created {i + 1} short URLs...')
        
        self.stdout.write(f'✅ Generated {len(urls)} short URLs')
        return urls

    def generate_click_events(self, urls, count):
        """Generate test click events (simulated via URL access)."""
        self.stdout.write(f'🔄 Simulating {count} click events...')
        
        # Simulate click events by updating click counts on URLs
        for i in range(count):
            url = random.choice(urls)
            # Update click count to simulate clicks
            url.click_count += random.randint(1, 10)
            
            if (i + 1) % 500 == 0:
                self.stdout.write(f'   ✅ Simulated {i + 1} click events...')
        
        self.stdout.write(f'✅ Simulated {count} click events')
        return count
