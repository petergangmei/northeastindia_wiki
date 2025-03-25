from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from tinymce.models import HTMLField

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
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='viewer')
    
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
        return reverse('category-detail', kwargs={'slug': self.slug})


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
    image = models.ImageField(upload_to='states/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('state-detail', kwargs={'slug': self.slug})


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
    featured_image = models.ImageField(upload_to='content/', blank=True, null=True)
    
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


class Article(ContentItem):
    """
    Main content type for general articles
    """
    references = models.TextField(blank=True, help_text="Sources and references")
    last_edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='edited_articles')
    
    def get_absolute_url(self):
        return reverse('article-detail', kwargs={'slug': self.slug})


class ArticleRevision(TimeStampedModel):
    """
    Revision history for articles
    """
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='revisions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_revisions')
    content = models.TextField()
    comment = models.CharField(max_length=255, blank=True, help_text="Brief explanation of the changes")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Revision of {self.article.title} at {self.created_at}"


class PendingEdit(TimeStampedModel):
    """
    Stores pending edits for already approved articles
    """
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='pending_edit')
    title = models.CharField(max_length=255, blank=True)
    content = HTMLField()
    excerpt = models.TextField(blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    references = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to='content/pending/', blank=True, null=True)
    
    # Relationships - stored as IDs to avoid M2M complexity
    categories_ids = models.JSONField(default=list, blank=True)
    tags_ids = models.JSONField(default=list, blank=True)
    states_ids = models.JSONField(default=list, blank=True)
    
    # Edit metadata
    editor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pending_edits')
    revision_comment = models.CharField(max_length=255, blank=True, help_text="Brief explanation of the changes")
    
    def __str__(self):
        return f"Pending edit for {self.article.title}"
    
    def apply_edit(self):
        """Apply this pending edit to the article"""
        # Store original values for reverting if needed
        original_review_status = self.article.review_status
        
        # Update basic fields
        if self.title:
            self.article.title = self.title
        self.article.content = self.content
        self.article.excerpt = self.excerpt
        self.article.meta_description = self.meta_description
        self.article.references = self.references
        
        # Update featured image if provided
        if self.featured_image:
            # If there was a previous image, mark it for deletion or archive it
            if self.article.featured_image:
                pass  # Handle old image if needed
            
            # Set the new image
            self.article.featured_image = self.featured_image
        
        # Update the article's last_edited_by
        self.article.last_edited_by = self.editor
        
        # Set review status back to pending
        self.article.review_status = 'pending'
        
        # Save the article
        self.article.save()
        
        # Update M2M relationships if IDs are provided
        if self.categories_ids:
            self.article.categories.clear()
            categories = Category.objects.filter(id__in=self.categories_ids)
            self.article.categories.add(*categories)
            
        if self.tags_ids:
            self.article.tags.clear()
            tags = Tag.objects.filter(id__in=self.tags_ids)
            self.article.tags.add(*tags)
            
        if self.states_ids:
            self.article.states.clear()
            states = State.objects.filter(id__in=self.states_ids)
            self.article.states.add(*states)
        
        # Create a revision record
        ArticleRevision.objects.create(
            article=self.article,
            user=self.editor,
            content=self.content,
            comment=self.revision_comment or "Applied pending edit"
        )
        
        # Delete this pending edit
        self.delete()
        
        return True


class Personality(ContentItem):
    """
    Content type for notable personalities
    """
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    birth_place = models.CharField(max_length=255, blank=True)
    notable_works = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Personalities'
    
    def get_absolute_url(self):
        return reverse('personality-detail', kwargs={'slug': self.slug})


class CulturalElement(ContentItem):
    """
    Content type for cultural elements like festivals, traditions, etc.
    """
    element_type = models.CharField(max_length=50, 
        choices=(
            ('festival', 'Festival'),
            ('tradition', 'Tradition'),
            ('art_form', 'Art Form'),
            ('craft', 'Craft'),
            ('cuisine', 'Cuisine'),
            ('attire', 'Traditional Attire'),
            ('music', 'Music'),
            ('dance', 'Dance'),
            ('language', 'Language'),
            ('other', 'Other'),
        )
    )
    seasonal = models.BooleanField(default=False, help_text="Is this element seasonal or periodic?")
    season_or_period = models.CharField(max_length=100, blank=True, help_text="If seasonal, specify when it occurs")
    
    def get_absolute_url(self):
        return reverse('cultural-element-detail', kwargs={'slug': self.slug})


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
