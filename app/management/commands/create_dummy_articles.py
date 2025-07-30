import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from app.models import Content, Category, Tag, State, UserProfile

class Command(BaseCommand):
    help = 'Creates dummy articles for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of articles to create')

    def handle(self, *args, **options):
        count = options['count']
        
        # Make sure we have the necessary data
        admin_user = self._get_or_create_admin()
        categories = self._get_or_create_categories()
        tags = self._get_or_create_tags()
        states = self._get_or_create_states()
        
        articles_created = 0
        
        # Create the articles
        for i in range(count):
            title = f"Northeast India Article {i+1}: {random.choice(self.sample_titles)}"
            slug = slugify(title)
            
            # Check if article with this slug already exists
            if Content.objects.filter(slug=slug).exists():
                self.stdout.write(self.style.WARNING(f"Article with slug '{slug}' already exists. Skipping."))
                continue
            
            # Create the article
            article = Content.objects.create(
                title=title,
                slug=slug,
                content=self._generate_content(),
                excerpt=f"This is a sample article about {random.choice(self.sample_topics)} in Northeast India.",
                content_type='article',
                author=admin_user,
                published=True,
                published_at=timezone.now(),
                review_status='approved',
                meta_description=f"Learn about {random.choice(self.sample_topics)} in Northeast India.",
                type_data={'references': 'Sample references for testing purposes'}
            )
            
            # Add categories, tags, and states
            article.categories.add(*random.sample(list(categories), k=random.randint(1, 3)))
            article.tags.add(*random.sample(list(tags), k=random.randint(2, 5)))
            article.states.add(*random.sample(list(states), k=random.randint(1, 2)))
            
            # Note: ArticleRevision model has been removed in favor of unified Content model
            
            articles_created += 1
            self.stdout.write(self.style.SUCCESS(f"Created article: {title}"))
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created {articles_created} articles"))

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
            'Cuisine', 'Craft', 'Religion', 'Language', 'Clothing'
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
    
    def _generate_content(self):
        """Generate dummy content for articles"""
        paragraphs = [
            "<h2>Introduction</h2><p>Northeast India is a region known for its rich cultural diversity, stunning landscapes, and unique traditions. This article explores some of the fascinating aspects of this vibrant region.</p>",
            "<h2>Cultural Heritage</h2><p>The cultural heritage of Northeast India is truly diverse, with numerous indigenous communities preserving their traditional practices, languages, and artistic expressions. From the Bihu dance of Assam to the Cheraw dance of Mizoram, the region's cultural landscape is a tapestry of unique traditions.</p>",
            "<h2>Natural Beauty</h2><p>The Northeast region is blessed with abundant natural beauty, including dense forests, rolling hills, and mighty rivers. The biodiversity hotspots in the region are home to numerous rare and endangered species, making it a paradise for nature enthusiasts and conservationists.</p>",
            "<h2>Traditional Crafts</h2><p>Handloom and handicrafts are an integral part of Northeast Indian identity. Each state has its distinctive textile traditions, with intricate patterns and techniques passed down through generations. Bamboo and cane crafts are particularly noteworthy for their utilitarian and artistic value.</p>",
            "<h2>Cuisine</h2><p>The food traditions of Northeast India are characterized by minimal use of spices, fresh ingredients, and fermentation techniques. From Assam's fish tenga to Nagaland's smoked pork with axone, the cuisines offer unique flavors that reflect the region's agricultural practices and cultural values.</p>",
            "<h2>Festivals</h2><p>Festivals in Northeast India are vibrant celebrations of community life, agricultural cycles, and spiritual beliefs. The Hornbill Festival of Nagaland, Bihu of Assam, and Cheiraoba of Manipur showcase the rich cultural traditions of the region through music, dance, sports, and communal feasting.</p>"
        ]
        
        # Randomly select 3-6 paragraphs and shuffle them
        selected_paragraphs = random.sample(paragraphs, k=random.randint(3, 6))
        random.shuffle(selected_paragraphs)
        
        # Add a conclusion
        selected_paragraphs.append("<h2>Conclusion</h2><p>The diverse cultural tapestry, natural beauty, and unique traditions of Northeast India make it a fascinating region to explore and understand. As we continue to document and celebrate this diversity, we contribute to the preservation of the rich heritage of this remarkable part of India.</p>")
        
        return "".join(selected_paragraphs)
    
    # Sample data for article generation
    sample_titles = [
        "Cultural Heritage of", "Traditional Practices in", "Exploring the Beauty of", 
        "Indigenous Communities of", "Festivals and Celebrations in", "Art Forms from",
        "Cuisine and Food Traditions of", "Historical Landmarks in", "Wildlife and Nature in",
        "Textile Traditions of", "Musical Heritage of", "Architectural Wonders of"
    ]
    
    sample_topics = [
        "cultural heritage", "traditional festivals", "indigenous crafts", 
        "textile traditions", "cuisine", "performing arts", "natural landscapes",
        "tribal communities", "historical sites", "folk music", "ancient temples",
        "biodiversity", "handloom weaving", "bamboo crafts", "traditional dance forms"
    ] 