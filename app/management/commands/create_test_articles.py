import random
import time
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.db import transaction
from faker import Faker
from app.models import Content, Category, Tag, State
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Creates realistic test articles using Faker for performance testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='Number of articles to create')
        parser.add_argument('--batch-size', type=int, default=50, help='Batch size for bulk operations')
        parser.add_argument('--min-words', type=int, default=200, help='Minimum words per article')
        parser.add_argument('--max-words', type=int, default=500, help='Maximum words per article')
        parser.add_argument('--clear', action='store_true', help='Clear existing test articles first')

    def handle(self, *args, **options):
        self.fake = Faker()
        
        count = options['count']
        batch_size = options['batch_size']
        min_words = options['min_words']
        max_words = options['max_words']
        
        start_time = time.time()
        
        # Initialize global slug tracking
        self.used_slugs = set()
        self._load_existing_slugs()
        
        # Clear existing test articles if requested
        if options['clear']:
            self._clear_test_articles()
            self.used_slugs = set()  # Reset after clearing
            self._load_existing_slugs()
        
        # Ensure we have necessary data
        admin_user = self._get_or_create_admin()
        categories = self._get_or_create_categories()
        tags = self._get_or_create_tags()
        states = self._get_or_create_states()
        
        self.stdout.write(self.style.SUCCESS(f"Starting creation of {count} articles..."))
        
        articles_created = 0
        articles_attempted = 0
        batch_articles = []
        
        # Generate articles in batches for better performance
        for i in range(count):
            articles_attempted += 1
            
            try:
                article_data = self._generate_article_data(
                    admin_user, min_words, max_words, i + 1
                )
                
                batch_articles.append(article_data)
                
                # Create batch when we reach batch_size or at the end
                if len(batch_articles) >= batch_size or i == count - 1:
                    created_count = self._create_article_batch(
                        batch_articles, categories, tags, states
                    )
                    articles_created += created_count
                    
                    # Progress report
                    self.stdout.write(
                        f"Progress: {articles_created}/{articles_attempted} articles created "
                        f"({(articles_created/count)*100:.1f}%)"
                    )
                    
                    batch_articles = []  # Reset batch
            
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Skipped article {i+1} due to error: {str(e)}")
                )
                continue
        
        end_time = time.time()
        duration = end_time - start_time
        
        success_rate = (articles_created / articles_attempted) * 100 if articles_attempted > 0 else 0
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {articles_created}/{articles_attempted} articles "
                f"({success_rate:.1f}% success rate) in {duration:.2f} seconds "
                f"({articles_created/duration:.1f} articles/sec)"
            )
        )

    def _load_existing_slugs(self):
        """Load existing slugs from database to avoid collisions"""
        existing_slugs = Content.objects.values_list('slug', flat=True)
        self.used_slugs.update(existing_slugs)
        self.stdout.write(f"Loaded {len(self.used_slugs)} existing slugs")

    def _clear_test_articles(self):
        """Remove existing test articles"""
        test_articles = Content.objects.filter(title__startswith='Test Article:')
        count = test_articles.count()
        test_articles.delete()
        self.stdout.write(self.style.WARNING(f"Cleared {count} existing test articles"))

    def _generate_unique_slug(self, title):
        """Generate a unique slug, handling collisions"""
        base_slug = slugify(title)
        if len(base_slug) > 250:  # Ensure slug fits in database field
            base_slug = base_slug[:250]
        
        slug = base_slug
        counter = 1
        
        # Keep trying until we find a unique slug
        while slug in self.used_slugs:
            slug = f"{base_slug}-{counter}"
            if len(slug) > 280:  # Database field limit
                # Truncate base slug to make room for counter
                truncated_base = base_slug[:270-len(str(counter))]
                slug = f"{truncated_base}-{counter}"
            counter += 1
            
            # Safety check to prevent infinite loops
            if counter > 10000:
                slug = f"{base_slug}-{self.fake.random_int(min=10000, max=99999)}"
                break
        
        # Add to used slugs set
        self.used_slugs.add(slug)
        return slug

    def _generate_article_data(self, admin_user, min_words, max_words, article_num):
        """Generate realistic article data using Faker"""
        
        # Generate article topic and title
        topic_type = random.choice(['cultural', 'historical', 'biographical', 'geographical'])
        
        if topic_type == 'cultural':
            title = f"Test Article: {self.fake.catch_phrase()} - Cultural Heritage of {self.fake.city()}"
        elif topic_type == 'historical':
            title = f"Test Article: The Historical Significance of {self.fake.city()} in Northeast India"
        elif topic_type == 'biographical':
            title = f"Test Article: {self.fake.name()} - A Notable Figure from Northeast India"
        else:  # geographical
            title = f"Test Article: Exploring the Natural Beauty of {self.fake.city()}"
        
        # Generate unique slug using the new method
        slug = self._generate_unique_slug(title)
        
        # Generate article content
        content = self._generate_article_content(topic_type, min_words, max_words)
        
        # Generate excerpt
        excerpt = self.fake.text(max_nb_chars=200)
        
        # Generate meta description
        meta_description = self.fake.text(max_nb_chars=150)
        
        # Generate info box data
        info_box_data = self._generate_info_box_data(topic_type)
        
        return {
            'title': title,
            'slug': slug,
            'content': content,
            'excerpt': excerpt,
            'content_type': 'article',
            'author': admin_user,
            'published': True,
            'published_at': timezone.now(),
            'review_status': 'approved',
            'meta_description': meta_description,
            'info_box_data': info_box_data,
        }

    def _generate_article_content(self, topic_type, min_words, max_words):
        """Generate realistic article content based on topic type"""
        
        target_words = random.randint(min_words, max_words)
        sections = random.randint(3, 6)  # Number of sections
        words_per_section = target_words // sections
        
        content = []
        
        # Introduction
        content.append("<h2>Introduction</h2>")
        content.append(f"<p>{self.fake.text(max_nb_chars=words_per_section * 5)}</p>")
        
        # Main sections based on topic type
        if topic_type == 'cultural':
            section_titles = [
                "Cultural Traditions", "Festivals and Celebrations", "Art and Crafts", 
                "Music and Dance", "Traditional Practices"
            ]
        elif topic_type == 'historical':
            section_titles = [
                "Historical Background", "Key Events", "Significance", 
                "Archaeological Evidence", "Legacy"
            ]
        elif topic_type == 'biographical':
            section_titles = [
                "Early Life and Background", "Career and Achievements", "Contributions", 
                "Recognition and Awards", "Personal Life"
            ]
        else:  # geographical
            section_titles = [
                "Geography and Location", "Natural Features", "Climate", 
                "Flora and Fauna", "Tourism and Accessibility"
            ]
        
        # Generate main sections
        selected_sections = random.sample(section_titles, min(sections - 2, len(section_titles)))
        
        for section_title in selected_sections:
            content.append(f"<h2>{section_title}</h2>")
            
            # Generate 1-2 paragraphs per section
            paragraphs = random.randint(1, 2)
            for _ in range(paragraphs):
                paragraph_text = self.fake.text(max_nb_chars=words_per_section * 5)
                content.append(f"<p>{paragraph_text}</p>")
        
        # Conclusion
        content.append("<h2>Conclusion</h2>")
        content.append(f"<p>{self.fake.text(max_nb_chars=words_per_section * 5)}</p>")
        
        return "".join(content)

    def _generate_info_box_data(self, topic_type):
        """Generate realistic info box data based on topic type"""
        
        if topic_type == 'cultural':
            return {
                'Type': 'Cultural Practice',
                'Region': self.fake.city(),
                'Origin': f"{self.fake.random_int(min=1200, max=1800)}s",
                'Language': random.choice(['Assamese', 'Bengali', 'Manipuri', 'Khasi', 'Mizo']),
                'Practitioners': f"{self.fake.random_int(min=1000, max=100000):,}"
            }
        elif topic_type == 'historical':
            return {
                'Period': f"{self.fake.random_int(min=1400, max=1900)}s",
                'Location': self.fake.city(),
                'Significance': 'Historical',
                'Date Established': self.fake.date_between(start_date='-300y', end_date='-50y').strftime('%Y'),
                'Current Status': random.choice(['Preserved', 'Ruins', 'Restored', 'Protected'])
            }
        elif topic_type == 'biographical':
            birth_date = self.fake.date_between(start_date='-100y', end_date='-20y')
            return {
                'Full Name': self.fake.name(),
                'Born': birth_date.strftime('%B %d, %Y'),
                'Birthplace': self.fake.city(),
                'Occupation': random.choice(['Writer', 'Activist', 'Artist', 'Leader', 'Scholar']),
                'Known for': self.fake.catch_phrase(),
                'Awards': random.choice(['Padma Shri', 'Sahitya Akademi', 'National Award', 'State Honor'])
            }
        else:  # geographical
            return {
                'Type': random.choice(['Hill Station', 'National Park', 'Lake', 'Mountain', 'Valley']),
                'Location': self.fake.city(),
                'Elevation': f"{self.fake.random_int(min=100, max=3000)} meters",
                'Area': f"{self.fake.random_int(min=10, max=1000)} km²",
                'Best Time to Visit': random.choice(['October-March', 'November-April', 'March-June']),
                'Nearest Airport': f"{self.fake.city()} Airport"
            }

    @transaction.atomic
    def _create_article_batch(self, batch_articles, categories, tags, states):
        """Create a batch of articles using bulk operations with error handling"""
        
        if not batch_articles:
            return 0
        
        try:
            # Convert article data to Content objects
            content_objects = []
            valid_articles = []
            
            for article_data in batch_articles:
                try:
                    content_objects.append(Content(**article_data))
                    valid_articles.append(article_data)
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Skipped invalid article data: {str(e)}")
                    )
                    continue
            
            if not content_objects:
                return 0
            
            # Bulk create articles
            created_articles = Content.objects.bulk_create(content_objects)
            
            # Add relationships (categories, tags, states) for each article
            for article in created_articles:
                try:
                    # Add random categories (1-3)
                    article_categories = random.sample(list(categories), k=random.randint(1, min(3, len(categories))))
                    article.categories.set(article_categories)
                    
                    # Add random tags (2-5)
                    article_tags = random.sample(list(tags), k=random.randint(2, min(5, len(tags))))
                    article.tags.set(article_tags)
                    
                    # Add random states (1-2)
                    article_states = random.sample(list(states), k=random.randint(1, min(2, len(states))))
                    article.states.set(article_states)
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to set relationships for article {article.slug}: {str(e)}")
                    )
                    continue
            
            return len(created_articles)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Batch creation failed: {str(e)}")
            )
            # Try creating articles one by one as fallback
            return self._create_articles_individually(batch_articles, categories, tags, states)

    def _create_articles_individually(self, batch_articles, categories, tags, states):
        """Fallback method to create articles one by one"""
        created_count = 0
        
        for article_data in batch_articles:
            try:
                # Create individual article
                article = Content.objects.create(**article_data)
                
                # Add relationships
                article_categories = random.sample(list(categories), k=random.randint(1, min(3, len(categories))))
                article.categories.set(article_categories)
                
                article_tags = random.sample(list(tags), k=random.randint(2, min(5, len(tags))))
                article.tags.set(article_tags)
                
                article_states = random.sample(list(states), k=random.randint(1, min(2, len(states))))
                article.states.set(article_states)
                
                created_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Failed to create individual article: {str(e)}")
                )
                continue
        
        return created_count

    def _get_or_create_admin(self):
        """Get or create an admin user for authoring articles"""
        try:
            admin = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            UserProfile.objects.create(
                user=admin,
                role='admin',
                bio='Site administrator',
                location='Northeast India',
                website='https://northeastindia.wiki'
            )
            self.stdout.write(self.style.SUCCESS("Created admin user"))
        return admin

    def _get_or_create_categories(self):
        """Get or create categories for the articles"""
        categories_data = [
            {'name': 'Culture', 'description': 'Cultural aspects of Northeast India'},
            {'name': 'History', 'description': 'Historical events and periods'},
            {'name': 'Food', 'description': 'Cuisine and food traditions'},
            {'name': 'Travel', 'description': 'Tourism and travel information'},
            {'name': 'Art', 'description': 'Art forms and artistic traditions'},
            {'name': 'Festivals', 'description': 'Celebrations and traditional festivals'},
            {'name': 'People', 'description': 'Notable personalities and communities'},
            {'name': 'Nature', 'description': 'Natural landscapes and wildlife'},
            {'name': 'Traditions', 'description': 'Traditional practices and customs'},
            {'name': 'Heritage', 'description': 'Cultural and historical heritage'},
        ]
        
        categories = []
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description']
                }
            )
            categories.append(cat)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {cat.name}"))
        
        return categories

    def _get_or_create_tags(self):
        """Get or create tags for the articles"""
        tag_names = [
            'Traditional', 'Modern', 'Heritage', 'Indigenous', 'Tribal',
            'Wildlife', 'Nature', 'Tourism', 'Dance', 'Music',
            'Cuisine', 'Craft', 'Religion', 'Language', 'Clothing',
            'Festival', 'Art', 'Architecture', 'Literature', 'History'
        ]
        
        tags = []
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            tags.append(tag)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created tag: {tag.name}"))
        
        return tags

    def _get_or_create_states(self):
        """Get or create Northeast Indian states"""
        states_data = [
            {
                'name': 'Assam',
                'description': 'Known for tea plantations and one-horned rhinoceros',
                'capital': 'Dispur',
                'languages': 'Assamese, Bengali, Bodo'
            },
            {
                'name': 'Meghalaya',
                'description': 'Known as the abode of clouds with living root bridges',
                'capital': 'Shillong',
                'languages': 'Khasi, Garo, English'
            },
            {
                'name': 'Manipur',
                'description': 'Known for Loktak Lake and classical dance forms',
                'capital': 'Imphal',
                'languages': 'Manipuri, English'
            },
            {
                'name': 'Arunachal Pradesh',
                'description': 'Largest Northeastern state with diverse tribal cultures',
                'capital': 'Itanagar',
                'languages': 'Nyishi, Adi, Galo, Apatani, English'
            },
            {
                'name': 'Nagaland',
                'description': 'Known for Hornbill Festival and tribal heritage',
                'capital': 'Kohima',
                'languages': 'Angami, Ao, Sumi, English'
            },
            {
                'name': 'Mizoram',
                'description': 'Known for bamboo forests and Cheraw dance',
                'capital': 'Aizawl',
                'languages': 'Mizo, English'
            },
            {
                'name': 'Tripura',
                'description': 'Known for royal heritage and natural beauty',
                'capital': 'Agartala',
                'languages': 'Bengali, Kokborok, English'
            },
            {
                'name': 'Sikkim',
                'description': 'Known for monasteries and mountain landscapes',
                'capital': 'Gangtok',
                'languages': 'Nepali, Bhutia, Lepcha, English'
            }
        ]
        
        states = []
        for state_data in states_data:
            state, created = State.objects.get_or_create(
                name=state_data['name'],
                defaults={
                    'slug': slugify(state_data['name']),
                    'description': state_data['description'],
                    'capital': state_data['capital'],
                    'languages': state_data['languages']
                }
            )
            states.append(state)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created state: {state.name}"))
        
        return states
    
#   # Basic usage - create 100 articles
#   python manage.py create_test_articles --count 100 --settings=core.settings.prod

#   # Create 1000 articles with custom word count
#   python manage.py create_test_articles --count 1000 --min-words 300 --max-words
#    600 --settings=core.settings.prod

#   # Clear old test articles and create new ones
#   python manage.py create_test_articles --count 500 --clear

#   # Custom batch size for memory optimization
#   python manage.py create_test_articles --count 2000 --batch-size 100

#python manage.py create_test_articles --count 10000 --batch-size 10 --settings=core.settings.prod