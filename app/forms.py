from django import forms
from django.utils.text import slugify
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from tinymce.widgets import TinyMCE
from .models import Content, Category, Tag, State

class CustomUserCreationForm(UserCreationForm):
    """
    Custom user registration form that includes email and terms agreement
    """
    email = forms.EmailField(required=True)
    agree_terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the terms to register.'}
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ArticleForm(forms.ModelForm):
    """
    Form for creating and editing articles
    """
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    revision_comment = forms.CharField(
        max_length=255, 
        required=False, 
        help_text="Brief explanation of changes (for revision history)",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Fixed typos, added new section, etc.'})
    )
    
    class Meta:
        model = Content
        fields = [
            'title', 'content', 'excerpt', 'categories', 'tags', 
            'states', 'featured_image', 'meta_description', 'content_type', 'type_data'
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.TextInput(attrs={'placeholder': 'Brief description for search engines'}),
            'type_data': forms.Textarea(attrs={'rows': 3, 'placeholder': 'JSON data for type-specific fields (e.g., {"references": "..."})'}),
            'content_type': forms.Select(choices=Content.CONTENT_TYPES),
        }
    
    def clean_title(self):
        """Ensure the title can generate a unique slug"""
        title = self.cleaned_data['title']
        slug = slugify(title)
        
        # If we're editing an existing article, exclude it from the unique check
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            # Check if any other article has the same slug
            existing = Content.objects.filter(slug=slug).exclude(pk=instance.pk).exists()
        else:
            # For new articles, simply check if the slug exists
            existing = Content.objects.filter(slug=slug).exists()
            
        if existing:
            raise forms.ValidationError("An article with a similar title already exists. Please choose a different title.")
        return title 