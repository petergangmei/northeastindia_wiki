from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import (
    Category, Tag, State, MediaItem, Comment, Contribution, Notification, Content
)
class TimeStampedModelAdmin(admin.ModelAdmin):
    """Base admin class for models inheriting from TimeStampedModel"""
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')


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


class ContentAdminForm(forms.ModelForm):
    """Custom form for Content admin to handle type_data as plain textarea"""
    
    class Meta:
        model = Content
        fields = '__all__'
    

@admin.register(Content)
class ContentAdmin(TimeStampedModelAdmin):
    form = ContentAdminForm
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
        
        
        base_fieldsets.append(('Metadata', {
            'fields': ('last_edited_by', 'created_at', 'updated_at')
        }))
        
        return base_fieldsets
    
    def save_model(self, request, obj, form, change):
        if change:
            obj.last_edited_by = request.user
        super().save_model(request, obj, form, change)
    
