from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from tinymce.models import HTMLField
from .fields import CompressedImageField

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    created and modified fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(models.Model):
    """
    Extended user profile with additional attributes and role-based permissions
    """
    USER_ROLES = (
        ('viewer', 'Viewer'),
        ('contributor', 'Contributor'),
        ('editor', 'Editor'),
        ('admin', 'Administrator'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='viewer')
    
    # Social media handles for enhanced sharing
    twitter_handle = models.CharField(max_length=50, blank=True, help_text="Twitter handle without @")
    linkedin_profile = models.URLField(blank=True, help_text="LinkedIn profile URL")
    facebook_profile = models.URLField(blank=True, help_text="Facebook profile URL")
    
    # Reputation and contribution tracking
    reputation_points = models.IntegerField(default=0)
    contribution_count = models.IntegerField(default=0)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse('app:profile', kwargs={'username': self.user.username})


class Category(TimeStampedModel):
    """
    Content categories for organizing articles
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('app:article-category', kwargs={'slug': self.slug})


class Tag(TimeStampedModel):
    """
    Tags for flexible content labeling and filtering
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('app:article-tag', kwargs={'slug': self.slug})


class State(TimeStampedModel):
    """
    Northeast Indian states for regional content organization
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField()
    capital = models.CharField(max_length=100)
    formation_date = models.DateField(null=True, blank=True)
    population = models.PositiveIntegerField(null=True, blank=True)
    area = models.PositiveIntegerField(help_text="Area in square kilometers", null=True, blank=True)
    languages = models.CharField(max_length=255, help_text="Comma-separated list of major languages", blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('app:state-detail', kwargs={'state_slug': self.slug})


class ContentItem(TimeStampedModel):
    """
    Abstract base class for all content types with common fields
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    content = HTMLField()
    excerpt = models.TextField(blank=True, help_text="A short summary of the content")
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Relationships
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='%(class)s_items')
    categories = models.ManyToManyField(Category, blank=True, related_name='%(class)s_items')
    tags = models.ManyToManyField(Tag, blank=True, related_name='%(class)s_items')
    states = models.ManyToManyField(State, blank=True, related_name='%(class)s_items')
    
    # SEO and metadata
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    featured_image = CompressedImageField(upload_to='content/', blank=True, null=True, quality=85, max_width=1200)
    
    # Moderation and review
    review_status = models.CharField(max_length=20, 
        choices=(
            ('draft', 'Draft'),
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('featured', 'Featured'),
        ), 
        default='draft'
    )
    review_notes = models.TextField(blank=True)
    
    class Meta:
        abstract = True
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        if self.published and not self.published_at:
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)












class MediaItem(TimeStampedModel):
    """
    Model for handling both external and local media with attribution
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Media can be either external or local
    file = models.FileField(upload_to='media/', blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    
    # Media type
    media_type = models.CharField(max_length=20, 
        choices=(
            ('image', 'Image'),
            ('video', 'Video'),
            ('audio', 'Audio'),
            ('document', 'Document'),
            ('other', 'Other'),
        ),
        default='image'
    )
    
    # Attribution and copyright
    creator = models.CharField(max_length=255, blank=True, help_text="Original creator or owner of the media")
    source = models.CharField(max_length=255, blank=True, help_text="Source of the media")
    license = models.CharField(max_length=100, blank=True, help_text="License type, e.g., CC BY-SA 4.0")
    
    # Relationships
    uploader = models.ForeignKey(User, on_delete=models.PROTECT, related_name='media_items')
    
    def __str__(self):
        return self.title
    
    @property
    def is_external(self):
        return bool(self.external_url and not self.file)
    
    def get_url(self):
        """
        Returns the URL for the media item, whether local or external
        """
        if self.file:
            return self.file.url
        return self.external_url
    
    def get_absolute_url(self):
        return reverse('media-detail', kwargs={'pk': self.pk})


class Comment(TimeStampedModel):
    """
    User comments on content items
    """
    content_type = models.CharField(max_length=20, 
        choices=(
            ('article', 'Article'),
            ('personality', 'Personality'),
            ('cultural', 'Cultural Element'),
        )
    )
    object_id = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username}"


class Contribution(TimeStampedModel):
    """
    Tracks user contributions for the reputation system
    """
    CONTRIBUTION_TYPES = (
        ('article_create', 'Created Article'),
        ('article_edit', 'Edited Article'),
        ('article_published', 'Published Article'),
        ('article_rejected', 'Rejected Article'),
        ('personality_create', 'Created Personality'),
        ('personality_edit', 'Edited Personality'),
        ('cultural_create', 'Created Cultural Element'),
        ('cultural_edit', 'Edited Cultural Element'),
        ('media_upload', 'Uploaded Media'),
        ('comment', 'Posted Comment'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    contribution_type = models.CharField(max_length=30, choices=CONTRIBUTION_TYPES)
    content_type = models.CharField(max_length=20, blank=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    points_earned = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_contributions')
    
    def __str__(self):
        return f"{self.user.username} - {self.contribution_type} - {self.created_at}"


class Notification(TimeStampedModel):
    """
    User notifications for system events
    """
    NOTIFICATION_TYPES = (
        ('comment', 'New Comment'),
        ('review', 'Content Review'),
        ('approval', 'Content Approved'),
        ('rejection', 'Content Rejected'),
        ('mention', 'User Mention'),
        ('system', 'System Notification'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    content_type = models.CharField(max_length=20, blank=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    message = models.TextField()
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"


class Content(TimeStampedModel):
    """
    Unified content model for all content types (articles, personalities, cultural elements)
    Optimized for scalability and performance
    """
    CONTENT_TYPES = (
        ('article', 'Article'),
        ('personality', 'Personality'),
        ('cultural', 'Cultural Element'),
    )
    
    REVIEW_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('featured', 'Featured'),
    )
    
    # Core fields (used by all content types)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    content = HTMLField()
    excerpt = models.TextField(blank=True, help_text="A short summary of the content")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    
    # Publishing and status
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='draft')
    review_notes = models.TextField(blank=True)
    
    # Relationships
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='content_items')
    categories = models.ManyToManyField(Category, blank=True, related_name='content_items')
    tags = models.ManyToManyField(Tag, blank=True, related_name='content_items')
    states = models.ManyToManyField(State, blank=True, related_name='content_items')
    
    # SEO and metadata
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    featured_image = CompressedImageField(upload_to='content/', blank=True, null=True, quality=85, max_width=1200)
    
    
    # Legacy support fields (will be moved to type_data eventually)
    last_edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='edited_content')
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['content_type', 'published']),
            models.Index(fields=['published_at']),
            models.Index(fields=['review_status']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        if self.published and not self.published_at:
            self.published_at = timezone.now()
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """
        Generate URL based on content type and context
        """
        # Get primary category and state for URL generation
        primary_category = self.categories.first()
        primary_state = self.states.first()
        
        # Content type specific URL patterns
        if self.content_type == 'personality':
            return reverse('app:personality-detail', kwargs={'slug': self.slug})
        elif self.content_type == 'cultural':
            return reverse('app:cultural-element-detail', kwargs={'slug': self.slug})
        else:  # article or default
            # Try to generate SEO-friendly URL based on category
            if primary_category and primary_state:
                category_slug = primary_category.slug
                state_slug = primary_state.slug
                
                # Map categories to URL patterns
                category_url_map = {
                    'personalities': 'app:seo-personalities-detail',
                    'culture': 'app:seo-culture-detail',
                    'festivals': 'app:seo-festivals-detail',
                    'places': 'app:seo-places-detail',
                    'heritage': 'app:seo-heritage-detail',
                    'history': 'app:seo-history-detail',
                    'traditional-crafts': 'app:seo-crafts-detail',
                    'traditional-arts': 'app:seo-crafts-detail',
                    'food': 'app:seo-food-detail',
                    'cuisine': 'app:seo-food-detail',
                    'music': 'app:seo-music-detail',
                    'folk-music': 'app:seo-music-detail',
                    'dance': 'app:seo-dance-detail',
                    'literature': 'app:seo-literature-detail',
                    'tribal-culture': 'app:seo-culture-detail',
                    'historical-sites': 'app:seo-heritage-detail',
                }
                
                url_name = category_url_map.get(category_slug)
                if url_name:
                    try:
                        return reverse(url_name, kwargs={
                            'state_slug': state_slug,
                            'slug': self.slug
                        })
                    except:
                        pass
            
            # Fallback to basic article URL
            return reverse('app:article-detail', kwargs={'slug': self.slug})
    
    def get_seo_title(self):
        """Generate SEO-optimized title"""
        components = [self.title]
        
        # Add state context
        primary_state = self.states.first()
        if primary_state:
            components.append(primary_state.name)
        
        # Add category context
        primary_category = self.categories.first()
        if primary_category:
            components.append(primary_category.name.title())
        
        # Add regional context
        components.append('Northeast India')
        
        return ' | '.join(components)
    
    def get_seo_description(self):
        """Generate SEO-optimized meta description"""
        if self.meta_description:
            return self.meta_description
        
        # Fallback to excerpt or truncated content
        if self.excerpt:
            return self.excerpt[:155] + '...' if len(self.excerpt) > 155 else self.excerpt
        
        # Generate from content (strip HTML)
        import re
        clean_content = re.sub(r'<[^>]+>', '', self.content)
        return (clean_content[:150] + '...') if len(clean_content) > 150 else clean_content
    
