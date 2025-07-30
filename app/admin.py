from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserProfile, Category, Tag, State, MediaItem, Comment, Contribution, Notification, Content
)

class TimeStampedModelAdmin(admin.ModelAdmin):
    """Base admin class for models inheriting from TimeStampedModel"""
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'reputation_points', 'contribution_count')
    list_filter = ('role', 'email_notifications')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    readonly_fields = ('reputation_points', 'contribution_count')


@admin.register(Category)
class CategoryAdmin(TimeStampedModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(TimeStampedModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(State)
class StateAdmin(TimeStampedModelAdmin):
    list_display = ('name', 'capital', 'formation_date', 'population')
    search_fields = ('name', 'description', 'capital')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('created_at',)




@admin.register(MediaItem)
class MediaItemAdmin(TimeStampedModelAdmin):
    list_display = ('title', 'media_type', 'is_external', 'uploader', 'created_at')
    list_filter = ('media_type', 'created_at')
    search_fields = ('title', 'description', 'creator', 'source')
    readonly_fields = ('created_at', 'updated_at', 'file_preview')
    
    def is_external(self, obj):
        return obj.is_external
    is_external.boolean = True
    is_external.short_description = 'External'
    
    def file_preview(self, obj):
        if obj.media_type == 'image':
            if obj.file:
                return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.file.url)
            elif obj.external_url:
                return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.external_url)
        return "No preview available"
    file_preview.short_description = 'Preview'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'media_type', 'uploader')
        }),
        ('Media Source', {
            'fields': ('file', 'external_url', 'file_preview')
        }),
        ('Attribution', {
            'fields': ('creator', 'source', 'license')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Comment)
class CommentAdmin(TimeStampedModelAdmin):
    list_display = ('user', 'comment_preview', 'content_type', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('user__username', 'comment')
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'


@admin.register(Contribution)
class ContributionAdmin(TimeStampedModelAdmin):
    list_display = ('user', 'contribution_type', 'points_earned', 'approved', 'created_at')
    list_filter = ('contribution_type', 'approved', 'created_at')
    search_fields = ('user__username', 'content_type')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(TimeStampedModelAdmin):
    list_display = ('user', 'notification_type', 'read', 'created_at')
    list_filter = ('notification_type', 'read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)


@admin.register(Content)
class ContentAdmin(TimeStampedModelAdmin):
    list_display = ('title', 'content_type', 'author', 'review_status', 'published', 'published_at')
    list_filter = ('content_type', 'review_status', 'published', 'published_at', 'created_at', 'categories', 'states')
    search_fields = ('title', 'content', 'excerpt', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags', 'states')
    readonly_fields = ('created_at', 'updated_at', 'last_edited_by')
    
    def get_fieldsets(self, request, obj=None):
        """Dynamic fieldsets based on content type"""
        base_fieldsets = [
            (None, {
                'fields': ('title', 'slug', 'author', 'content_type', 'content', 'excerpt')
            }),
            ('Publication', {
                'fields': ('published', 'published_at')
            }),
            ('Categorization', {
                'fields': ('categories', 'tags', 'states')
            }),
            ('SEO and Media', {
                'fields': ('meta_description', 'featured_image')
            }),
            ('Review', {
                'fields': ('review_status', 'review_notes')
            }),
        ]
        
        # Add type-specific fieldsets based on content_type
        if obj and obj.content_type == 'personality':
            base_fieldsets.insert(-2, ('Personality Data (JSON)', {
                'fields': ('type_data',),
                'description': 'Store personality-specific data: {"birth_date": "1963-06-09", "death_date": null, "birth_place": "Kentucky", "notable_works": "..."}'
            }))
        elif obj and obj.content_type == 'cultural':
            base_fieldsets.insert(-2, ('Cultural Data (JSON)', {
                'fields': ('type_data',),
                'description': 'Store cultural-specific data: {"element_type": "festival", "seasonal": true, "season_or_period": "Winter"}'
            }))
        elif obj and obj.content_type == 'article':
            base_fieldsets.insert(-2, ('Article Data (JSON)', {
                'fields': ('type_data',),
                'description': 'Store article-specific data: {"references": "..."}'
            }))
        else:
            # For new objects or unknown types
            base_fieldsets.insert(-2, ('Type-Specific Data (JSON)', {
                'fields': ('type_data',),
                'description': 'Store type-specific data as JSON. Format depends on content_type.'
            }))
        
        base_fieldsets.append(('Metadata', {
            'fields': ('last_edited_by', 'created_at', 'updated_at')
        }))
        
        return base_fieldsets
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.last_edited_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form based on content type"""
        form = super().get_form(request, obj, **kwargs)
        
        # Add help text for type_data field based on content_type
        if obj:
            if obj.content_type == 'personality':
                form.base_fields['type_data'].help_text = 'Example: {"birth_date": "1963-06-09", "death_date": null, "birth_place": "Owensboro, Kentucky", "notable_works": "Pirates of the Caribbean, Edward Scissorhands"}'
            elif obj.content_type == 'cultural':
                form.base_fields['type_data'].help_text = 'Example: {"element_type": "festival", "seasonal": true, "season_or_period": "Winter solstice"}'
            elif obj.content_type == 'article':
                form.base_fields['type_data'].help_text = 'Example: {"references": "1. Source A\n2. Source B"}'
        
        return form
