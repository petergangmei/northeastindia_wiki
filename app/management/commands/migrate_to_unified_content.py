from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import Article, Personality, CulturalElement, Content

class Command(BaseCommand):
    help = 'Migrates existing Article, Personality, and CulturalElement data to unified Content model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be modified'))
        
        # Count existing data
        article_count = Article.objects.count()
        personality_count = Personality.objects.count()
        cultural_count = CulturalElement.objects.count()
        existing_content_count = Content.objects.count()
        
        self.stdout.write(f"Found {article_count} articles, {personality_count} personalities, {cultural_count} cultural elements")
        self.stdout.write(f"Existing unified content entries: {existing_content_count}")
        
        if existing_content_count > 0:
            self.stdout.write(self.style.WARNING(
                f"Warning: Content table already has {existing_content_count} entries. "
                "This migration may create duplicates if run multiple times."
            ))
        
        if not dry_run:
            response = input("Continue with migration? (yes/no): ")
            if response.lower() != 'yes':
                self.stdout.write("Migration cancelled.")
                return
        
        migrated_count = 0
        
        try:
            with transaction.atomic():
                # Migrate Articles
                migrated_count += self._migrate_articles(dry_run)
                
                # Migrate Personalities  
                migrated_count += self._migrate_personalities(dry_run)
                
                # Migrate Cultural Elements
                migrated_count += self._migrate_cultural_elements(dry_run)
                
                if dry_run:
                    self.stdout.write(self.style.SUCCESS(f"DRY RUN: Would migrate {migrated_count} items"))
                    raise transaction.TransactionManagementError("Dry run - rolling back")
                else:
                    self.stdout.write(self.style.SUCCESS(f"Successfully migrated {migrated_count} items to unified Content model"))
                    
        except transaction.TransactionManagementError:
            if not dry_run:
                raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Migration failed: {str(e)}"))
            raise

    def _migrate_articles(self, dry_run):
        """Migrate Article objects to Content"""
        articles = Article.objects.all()
        count = 0
        
        for article in articles:
            if not dry_run:
                # Check if already migrated (by slug)
                if Content.objects.filter(slug=article.slug).exists():
                    self.stdout.write(self.style.WARNING(f"Skipping article '{article.title}' - already exists in Content"))
                    continue
                
                content = Content.objects.create(
                    title=article.title,
                    slug=article.slug,
                    content=article.content,
                    excerpt=article.excerpt,
                    content_type='article',
                    published=article.published,
                    published_at=article.published_at,
                    review_status=article.review_status,
                    review_notes=article.review_notes,
                    author=article.author,
                    meta_description=article.meta_description,
                    featured_image=article.featured_image,
                    last_edited_by=article.last_edited_by,
                    type_data={
                        'references': article.references,
                    },
                    created_at=article.created_at,
                    updated_at=article.updated_at,
                )
                
                # Copy relationships
                content.categories.set(article.categories.all())
                content.tags.set(article.tags.all())
                content.states.set(article.states.all())
                
            count += 1
            if not dry_run:
                self.stdout.write(f"Migrated article: {article.title}")
            else:
                self.stdout.write(f"Would migrate article: {article.title}")
        
        return count

    def _migrate_personalities(self, dry_run):
        """Migrate Personality objects to Content"""
        personalities = Personality.objects.all()
        count = 0
        
        for personality in personalities:
            if not dry_run:
                # Check if already migrated (by slug)
                if Content.objects.filter(slug=personality.slug).exists():
                    self.stdout.write(self.style.WARNING(f"Skipping personality '{personality.title}' - already exists in Content"))
                    continue
                
                # Prepare type_data
                type_data = {}
                if personality.birth_date:
                    type_data['birth_date'] = personality.birth_date.strftime('%Y-%m-%d')
                if personality.death_date:
                    type_data['death_date'] = personality.death_date.strftime('%Y-%m-%d')
                if personality.birth_place:
                    type_data['birth_place'] = personality.birth_place
                if personality.notable_works:
                    type_data['notable_works'] = personality.notable_works
                
                content = Content.objects.create(
                    title=personality.title,
                    slug=personality.slug,
                    content=personality.content,
                    excerpt=personality.excerpt,
                    content_type='personality',
                    published=personality.published,
                    published_at=personality.published_at,
                    review_status=personality.review_status,
                    review_notes=personality.review_notes,
                    author=personality.author,
                    meta_description=personality.meta_description,
                    featured_image=personality.featured_image,
                    type_data=type_data,
                    created_at=personality.created_at,
                    updated_at=personality.updated_at,
                )
                
                # Copy relationships
                content.categories.set(personality.categories.all())
                content.tags.set(personality.tags.all())
                content.states.set(personality.states.all())
                
            count += 1
            if not dry_run:
                self.stdout.write(f"Migrated personality: {personality.title}")
            else:
                self.stdout.write(f"Would migrate personality: {personality.title}")
        
        return count

    def _migrate_cultural_elements(self, dry_run):
        """Migrate CulturalElement objects to Content"""
        cultural_elements = CulturalElement.objects.all()
        count = 0
        
        for element in cultural_elements:
            if not dry_run:
                # Check if already migrated (by slug)
                if Content.objects.filter(slug=element.slug).exists():
                    self.stdout.write(self.style.WARNING(f"Skipping cultural element '{element.title}' - already exists in Content"))
                    continue
                
                content = Content.objects.create(
                    title=element.title,
                    slug=element.slug,
                    content=element.content,
                    excerpt=element.excerpt,
                    content_type='cultural',
                    published=element.published,
                    published_at=element.published_at,
                    review_status=element.review_status,
                    review_notes=element.review_notes,
                    author=element.author,
                    meta_description=element.meta_description,
                    featured_image=element.featured_image,
                    type_data={
                        'element_type': element.element_type,
                        'seasonal': element.seasonal,
                        'season_or_period': element.season_or_period,
                    },
                    created_at=element.created_at,
                    updated_at=element.updated_at,
                )
                
                # Copy relationships
                content.categories.set(element.categories.all())
                content.tags.set(element.tags.all())
                content.states.set(element.states.all())
                
            count += 1
            if not dry_run:
                self.stdout.write(f"Migrated cultural element: {element.title}")
            else:
                self.stdout.write(f"Would migrate cultural element: {element.title}")
        
        return count