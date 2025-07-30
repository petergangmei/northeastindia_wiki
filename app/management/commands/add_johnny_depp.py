from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from datetime import date
from app.models import Personality, Category, Tag, State, UserProfile

class Command(BaseCommand):
    help = 'Adds Johnny Depp as a sample personality entry'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user = self._get_or_create_admin()
        
        # Check if Johnny Depp already exists
        if Personality.objects.filter(slug='johnny-depp').exists():
            self.stdout.write(self.style.WARNING("Johnny Depp entry already exists. Skipping."))
            return
        
        # Get or create necessary categories and tags
        personality_category = self._get_or_create_category()
        tags = self._get_or_create_tags()
        
        # Create Johnny Depp personality entry
        johnny_depp = Personality.objects.create(
            title="Johnny Depp",
            slug="johnny-depp",
            content=self._get_johnny_depp_content(),
            excerpt="American actor and musician known for his versatile roles in films like Pirates of the Caribbean and Edward Scissorhands.",
            birth_date=date(1963, 6, 9),
            birth_place="Owensboro, Kentucky, U.S.",
            notable_works="Pirates of the Caribbean series, Edward Scissorhands, Charlie and the Chocolate Factory, Alice in Wonderland, What's Eating Gilbert Grape",
            author=admin_user,
            published=True,
            published_at=timezone.now(),
            review_status='approved',
            meta_description="Johnny Depp - American actor and musician known for his distinctive character portrayals and versatile acting career."
        )
        
        # Add category and tags
        johnny_depp.categories.add(personality_category)
        johnny_depp.tags.add(*tags)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created Johnny Depp personality entry"))

    def _get_or_create_admin(self):
        """Get or create an admin user"""
        try:
            admin = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            UserProfile.objects.get_or_create(
                user=admin,
                defaults={
                    'role': 'admin',
                    'bio': 'Site administrator',
                    'location': 'Northeast India',
                    'website': 'https://northeastindia.wiki'
                }
            )
            self.stdout.write(self.style.SUCCESS("Created admin user"))
        return admin

    def _get_or_create_category(self):
        """Get or create personalities category"""
        category, created = Category.objects.get_or_create(
            name='Personalities',
            defaults={
                'slug': 'personalities',
                'description': 'Notable personalities and public figures'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created Personalities category"))
        return category

    def _get_or_create_tags(self):
        """Get or create relevant tags"""
        tag_names = ['Actor', 'Musician', 'Celebrity', 'Hollywood', 'Entertainment']
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

    def _get_johnny_depp_content(self):
        """Generate content for Johnny Depp entry"""
        return """
        <h2>Early Life</h2>
        <p>John Christopher Depp II was born on June 9, 1963, in Owensboro, Kentucky, U.S. He is an American actor and musician known for his versatile and eccentric character portrayals in a wide range of films.</p>
        
        <h2>Career</h2>
        <p>Depp began his career as a musician performing in several amateur rock bands before making his feature film debut in the horror film A Nightmare on Elm Street (1984). He then acted in Platoon (1986) before rising to prominence as a teen idol on the television series 21 Jump Street (1987–1990).</p>
        
        <h2>Notable Works</h2>
        <p>Some of his most acclaimed performances include:</p>
        <ul>
            <li>Captain Jack Sparrow in the Pirates of the Caribbean series</li>
            <li>Edward Scissorhands (1990)</li>
            <li>What's Eating Gilbert Grape (1993)</li>
            <li>Charlie and the Chocolate Factory (2005)</li>
            <li>Alice in Wonderland (2010)</li>
            <li>Sweeney Todd: The Demon Barber of Fleet Street (2007)</li>
        </ul>
        
        <h2>Recognition</h2>
        <p>Depp has received multiple accolades, including a Golden Globe Award as well as nominations for three Academy Awards and two BAFTA awards. His films have grossed over $3.7 billion worldwide, making him one of Hollywood's most bankable stars.</p>
        
        <h2>Personal Life</h2>
        <p>Beyond acting, Depp is also an accomplished musician and has played guitar for various artists. He is known for his distinctive style and has become a cultural icon for his unique approach to character development.</p>
        """