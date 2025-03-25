from django import forms
from django.utils.text import slugify
from tinymce.widgets import TinyMCE
from .models import Article, ArticleRevision, Category, Tag, State

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
        model = Article
        fields = [
            'title', 'content', 'excerpt', 'categories', 'tags', 
            'states', 'featured_image', 'meta_description', 'references'
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.TextInput(attrs={'placeholder': 'Brief description for search engines'}),
            'references': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List your sources and references here'}),
        }
    
    def clean_title(self):
        """Ensure the title can generate a unique slug"""
        title = self.cleaned_data['title']
        slug = slugify(title)
        
        # If we're editing an existing article, exclude it from the unique check
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            # Check if any other article has the same slug
            existing = Article.objects.filter(slug=slug).exclude(pk=instance.pk).exists()
        else:
            # For new articles, simply check if the slug exists
            existing = Article.objects.filter(slug=slug).exists()
            
        if existing:
            raise forms.ValidationError("An article with a similar title already exists. Please choose a different title.")
        return title 