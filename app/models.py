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
    featured_image = CompressedImageField(upload_to='content/', blank=True, null=True, max_width=1200, target_size_kb=80)
    
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
    
    PROTECTION_LEVELS = (
        ('unprotected', 'Unprotected'),        # Anyone with contributor+ role can edit
        ('semi_protected', 'Semi-protected'),   # Requires autoconfirmed status
        ('extended_confirmed', 'Extended Confirmed Protected'),  # Requires extended-confirmed status
        ('pending_changes', 'Pending Changes'),  # Edits require review before going live
        ('protected', 'Protected'),             # Only editors and admins can edit
        ('fully_protected', 'Fully Protected'), # Only admins can edit
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
    
    # Collaborative editing and protection
    protection_level = models.CharField(max_length=20, choices=PROTECTION_LEVELS, default='unprotected', help_text="Wikipedia-style protection level")
    protection_reason = models.TextField(blank=True, help_text="Reason for protection (vandalism, edit wars, etc.)")
    protection_expires = models.DateTimeField(null=True, blank=True, help_text="When protection expires (if temporary)")
    protected_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='protected_content', help_text="Admin who applied protection")
    
    # Edit tracking for collaboration
    edit_count = models.PositiveIntegerField(default=0, help_text="Total number of approved edits")
    watchers = models.ManyToManyField(User, blank=True, related_name='watched_content', help_text="Users watching this content for changes")
    
    # Relationships
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='content_items')
    categories = models.ManyToManyField(Category, blank=True, related_name='content_items')
    tags = models.ManyToManyField(Tag, blank=True, related_name='content_items')
    states = models.ManyToManyField(State, blank=True, related_name='content_items')
    
    # SEO and metadata
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    featured_image = CompressedImageField(upload_to='content/', blank=True, null=True, max_width=1200, target_size_kb=80)
    
    # Structured data for info boxes (stores label-value pairs as JSON)
    info_box_data = models.JSONField(default=dict, blank=True, help_text="Structured data for info box display (e.g., {'Name': 'Peter', 'Age': '25'})")
    
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
    
    def get_pending_revision(self):
        """Get the current pending revision if any"""
        return self.revisions.filter(status='pending_review').first()
    
    def has_pending_revision(self):
        """Check if there's a pending revision"""
        return self.revisions.filter(status='pending_review').exists()
    
    def get_latest_draft(self, user):
        """Get the latest draft revision for a specific user"""
        return self.revisions.filter(status='draft', editor=user).first()
    
    def get_active_revision(self):
        """Get the currently active (published) revision"""
        return self.revisions.filter(status='approved').first()
    
    def has_active_revision(self):
        """Check if there's an active revision"""
        return self.revisions.filter(status='approved').exists()
    
    def get_revision_status_summary(self):
        """Get a summary of revision statuses"""
        summary = {
            'total_revisions': self.revisions.count(),
            'draft_count': self.revisions.filter(status='draft').count(),
            'pending_count': self.revisions.filter(status='pending_review').count(),
            'approved_count': self.revisions.filter(status='approved').count(),
            'rejected_count': self.revisions.filter(status='rejected').count(),
            'active_revision': self.get_active_revision(),
            'pending_revision': self.get_pending_revision(),
        }
        return summary
    
    def can_be_edited_by(self, user):
        """
        Check if a user can edit this content - Wikipedia-style collaborative editing
        """
        if not user.is_authenticated:
            return False
        
        # Get user profile and role
        try:
            user_profile = user.profile
            user_role = user_profile.role
        except:
            # If no profile exists, treat as viewer
            user_role = 'viewer'
        
        # Staff users and admins can always edit
        if user.is_staff or user_role == 'admin':
            return True
        
        # Check protection level
        if self.protection_level == 'fully_protected':
            # Only admins can edit fully protected content
            return user_role == 'admin'
        
        elif self.protection_level == 'protected':
            # Only editors and admins can edit protected content
            return user_role in ['editor', 'admin']
        
        elif self.protection_level == 'extended_confirmed':
            # Only extended-confirmed users and above can edit
            return user_role in ['extended_confirmed', 'reviewer', 'editor', 'admin']
        
        elif self.protection_level == 'pending_changes':
            # All registered users can edit, but changes need approval
            return user_role in ['contributor', 'autoconfirmed', 'extended_confirmed', 'reviewer', 'editor', 'admin']
        
        elif self.protection_level == 'semi_protected':
            # Requires autoconfirmed status
            return user_role in ['autoconfirmed', 'extended_confirmed', 'reviewer', 'editor', 'admin']
        
        else:  # unprotected
            # Any contributor or higher can edit unprotected content
            return user_role in ['contributor', 'autoconfirmed', 'extended_confirmed', 'reviewer', 'editor', 'admin']
    
    def needs_pending_changes_review(self, user):
        """
        Check if edits by this user need pending changes review
        """
        if self.protection_level != 'pending_changes':
            return False
        
        try:
            user_profile = user.profile
            # Reviewers, editors, and admins don't need review
            return user_profile.role not in ['reviewer', 'editor', 'admin']
        except:
            return True
    
    def get_public_content(self):
        """
        Get content that should be shown to public/non-reviewers
        For pending changes protection, this returns the last approved version
        """
        if self.protection_level == 'pending_changes':
            # Return last approved revision content
            approved_revision = self.revisions.filter(status='approved').first()
            if approved_revision:
                return {
                    'title': approved_revision.title,
                    'content': approved_revision.content_text,
                    'excerpt': approved_revision.excerpt,
                    'meta_description': approved_revision.meta_description,
                    'featured_image': approved_revision.featured_image,
                    'info_box_data': approved_revision.info_box_data,
                }
        
        # For all other protection levels, return current content
        return {
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'meta_description': self.meta_description,
            'featured_image': self.featured_image,
            'info_box_data': self.info_box_data,
        }
    
    def get_live_content(self):
        """
        Get the live content including pending changes (for reviewers)
        """
        return {
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'meta_description': self.meta_description,
            'featured_image': self.featured_image,
            'info_box_data': self.info_box_data,
        }
    
    def has_pending_changes(self):
        """
        Check if there are pending changes waiting for review
        """
        if self.protection_level != 'pending_changes':
            return False
        
        return self.revisions.filter(status='pending_review').exists()
    
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


class ContentRevision(TimeStampedModel):
    """
    Model to store content revisions and pending edits
    Enables draft workflow where contributor edits require admin approval
    """
    REVISION_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('sighted', 'Sighted'),  # Flagged revisions - basic review
        ('flagged', 'Flagged'),  # Flagged revisions - quality review
    )
    
    # Link to the original content
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='revisions')
    
    # Revision metadata
    editor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='content_revisions')
    revision_comment = models.CharField(max_length=255, blank=True, help_text="Brief explanation of changes")
    status = models.CharField(max_length=20, choices=REVISION_STATUS_CHOICES, default='draft')
    
    # Content fields (snapshot of changes)
    title = models.CharField(max_length=255)
    content_text = HTMLField()  # Using different name to avoid confusion with FK
    excerpt = models.TextField(blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    featured_image = CompressedImageField(upload_to='content/revisions/', blank=True, null=True, max_width=1200, target_size_kb=80)
    
    # Structured data for info boxes
    info_box_data = models.JSONField(default=dict, blank=True, null=True)
    
    # Relationships (stored as JSON for flexibility)
    categories_data = models.JSONField(default=list, blank=True, help_text="List of category IDs")
    tags_data = models.JSONField(default=list, blank=True, help_text="List of tag IDs") 
    states_data = models.JSONField(default=list, blank=True, help_text="List of state IDs")
    
    # Review metadata
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_revisions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Flagged revisions support
    is_stable = models.BooleanField(default=False, help_text="Is this the stable/public version?")
    quality_level = models.IntegerField(default=0, help_text="Quality level (0=basic, 1=good, 2=featured)")
    sighted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='sighted_revisions', help_text="User who sighted this revision")
    sighted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['editor']),
        ]
    
    def __str__(self):
        return f"Revision of {self.content.title} by {self.editor.username} - {self.status}"
    
    def apply_to_content(self):
        """
        Apply this revision to the original content object
        Should only be called when revision is approved
        """
        if self.status != 'approved':
            raise ValueError("Only approved revisions can be applied")
        
        # Update the content object
        self.content.title = self.title
        self.content.content = self.content_text
        self.content.excerpt = self.excerpt
        self.content.meta_description = self.meta_description
        self.content.info_box_data = self.info_box_data
        self.content.last_edited_by = self.editor
        
        if self.featured_image:
            self.content.featured_image = self.featured_image
        
        # Update relationships
        if self.categories_data:
            self.content.categories.set(self.categories_data)
        if self.tags_data:
            self.content.tags.set(self.tags_data)
        if self.states_data:
            self.content.states.set(self.states_data)
        
        self.content.save()
        
        # Update revision metadata
        self.reviewed_at = timezone.now()
        self.save()
    
    def get_changes_summary(self):
        """
        Generate a summary of changes compared to the original content
        """
        changes = []
        
        if self.title != self.content.title:
            changes.append(f"Title: '{self.content.title}' → '{self.title}'")
        
        if self.content_text != self.content.content:
            changes.append("Content modified")
        
        if self.excerpt != self.content.excerpt:
            changes.append("Excerpt modified")
        
        if self.info_box_data != self.content.info_box_data:
            changes.append("Info box data modified")
        
        if not changes:
            changes.append("No significant changes detected")
        
        return changes


class DeletionRequest(TimeStampedModel):
    """
    Model to handle deletion requests for content (speedy, PROD, AfD)
    """
    DELETION_TYPES = (
        ('speedy', 'Speedy Deletion'),
        ('prod', 'Proposed Deletion (PROD)'),
        ('afd', 'Articles for Deletion (AfD)'),
    )
    
    DELETION_REASONS = (
        ('spam', 'Spam or advertising'),
        ('copyright', 'Copyright violation'),
        ('vandalism', 'Vandalism'),
        ('notability', 'Fails notability requirements'),
        ('sources', 'Lacks reliable sources'),
        ('maintenance', 'Technical maintenance'),
        ('duplicate', 'Duplicate content'),
        ('attack', 'Attack page or defamatory'),
        ('other', 'Other (specify in reason)'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved for Deletion'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('expired', 'Expired'),
    )
    
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='deletion_requests')
    requester = models.ForeignKey(User, on_delete=models.PROTECT, related_name='deletion_requests')
    deletion_type = models.CharField(max_length=10, choices=DELETION_TYPES)
    reason_code = models.CharField(max_length=20, choices=DELETION_REASONS)
    reason_text = models.TextField(help_text="Detailed explanation for deletion request")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_deletions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # For AfD discussions
    discussion_started = models.BooleanField(default=False)
    discussion_ends = models.DateTimeField(null=True, blank=True, help_text="When AfD discussion period ends")
    
    # For PROD grace period
    grace_period_ends = models.DateTimeField(null=True, blank=True, help_text="When PROD grace period ends")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['deletion_type', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_deletion_type_display()} request for {self.content.title}"
    
    def can_be_reviewed_by(self, user):
        """Check if user can review this deletion request"""
        try:
            profile = user.profile
            if self.deletion_type == 'speedy':
                # Only admins can approve speedy deletions
                return profile.role == 'admin'
            elif self.deletion_type in ['prod', 'afd']:
                # Admins and editors can review PROD and AfD
                return profile.role in ['editor', 'admin']
        except:
            pass
        return False
    
    def get_time_remaining(self):
        """Get time remaining for grace period or discussion"""
        from django.utils import timezone
        
        if self.deletion_type == 'prod' and self.grace_period_ends:
            if timezone.now() < self.grace_period_ends:
                remaining = self.grace_period_ends - timezone.now()
                return f"{remaining.days} days, {remaining.seconds // 3600} hours"
        elif self.deletion_type == 'afd' and self.discussion_ends:
            if timezone.now() < self.discussion_ends:
                remaining = self.discussion_ends - timezone.now()
                return f"{remaining.days} days, {remaining.seconds // 3600} hours"
        return None


class DeletionDiscussion(TimeStampedModel):
    """
    Model for AfD discussion comments
    """
    VOTE_CHOICES = (
        ('keep', 'Keep'),
        ('delete', 'Delete'),
        ('merge', 'Merge'),
        ('redirect', 'Redirect'),
        ('comment', 'Comment only'),
    )
    
    deletion_request = models.ForeignKey(DeletionRequest, on_delete=models.CASCADE, related_name='discussion_comments')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='deletion_votes')
    vote = models.CharField(max_length=10, choices=VOTE_CHOICES, default='comment')
    comment = models.TextField()
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.vote} on {self.deletion_request.content.title}"
