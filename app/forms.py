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
    content = forms.CharField(widget=TinyMCE(attrs={
        'cols': 80, 
        'rows': 30,
        'class': 'form-control'
    }, mce_attrs={
        'theme': 'silver',
        'height': 500,
        'menubar': True,
        'plugins': [
            'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
            'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
            'insertdatetime', 'media', 'table', 'paste', 'code', 'help', 'wordcount'
        ],
        'toolbar': [
            'undo redo | blocks | bold italic underline strikethrough | '
            'alignleft aligncenter alignright alignjustify | '
            'bullist numlist outdent indent | removeformat | help',
            'link unlink anchor | image media | table | '
            'charmap emoticons | preview | searchreplace | '
            'visualblocks code fullscreen'
        ],
        'block_formats': 'Paragraph=p; Heading 1=h1; Heading 2=h2; Heading 3=h3; Heading 4=h4; Heading 5=h5; Heading 6=h6; Preformatted=pre',
        'content_style': '''
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
                font-size: 16px;
                line-height: 1.6;
                color: #151b25;
                max-width: none;
                margin: 0;
                padding: 20px;
            }
            h1, h2, h3, h4, h5, h6 { 
                font-family: 'Georgia', serif;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
                color: #151b25;
                border-bottom: 1px solid #dee2e6;
                padding-bottom: 0.3em;
            }
            h1 { font-size: 2em; }
            h2 { font-size: 1.5em; }
            h3 { font-size: 1.3em; }
            h4 { font-size: 1.1em; }
            p { margin-bottom: 1em; text-align: justify; }
            blockquote { 
                border-left: 4px solid #e10032;
                margin: 1em 0;
                padding: 0.5em 1em;
                background: #f8f9fa;
                font-style: italic;
            }
            code { 
                background: #f8f9fa;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: 'Monaco', 'Consolas', monospace;
            }
            pre { 
                background: #f8f9fa;
                padding: 1em;
                border-radius: 5px;
                overflow-x: auto;
                border-left: 4px solid #151b25;
            }
            a { color: #0645ad; text-decoration: none; }
            a:hover { text-decoration: underline; }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }
            table, th, td {
                border: 1px solid #dee2e6;
            }
            th, td {
                padding: 0.75em;
                text-align: left;
            }
            th {
                background: #f8f9fa;
                font-weight: 600;
            }
        ''',
        'paste_as_text': True,
        'paste_word_valid_elements': 'b,strong,i,em,h1,h2,h3,h4,h5,h6,p,br,ul,ol,li,a[href],blockquote',
        'invalid_elements': 'script,style,font,center',
        'extended_valid_elements': 'a[href|target|title|class],img[src|alt|title|width|height|class],div[class|id],span[class|id],p[class],h1[class|id],h2[class|id],h3[class|id],h4[class|id],h5[class|id],h6[class|id]',
        'image_advtab': True,
        'image_caption': True,
        'link_target_list': [
            {'title': 'Same window', 'value': ''},
            {'title': 'New window', 'value': '_blank'}
        ],
        'table_default_attributes': {
            'class': 'table table-bordered'
        },
        'table_default_styles': {},
        'autocorrect': True,
        'browser_spellcheck': True,
        'contextmenu': 'link image table',
        'resize': True,
        'statusbar': True,
        'branding': False,
        'promotion': False
    }))
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
            'states', 'featured_image', 'meta_description', 'content_type'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter a descriptive title for your article',
                'maxlength': 255,
                'class': 'form-control'
            }),
            'excerpt': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write a brief summary that will appear in search results and previews...',
                'maxlength': 500,
                'class': 'form-control'
            }),
            'meta_description': forms.TextInput(attrs={
                'placeholder': 'Brief description that appears in Google search results',
                'maxlength': 160,
                'class': 'form-control'
            }),
            'content_type': forms.Select(choices=Content.CONTENT_TYPES, attrs={
                'class': 'form-select'
            }),
            'categories': forms.SelectMultiple(attrs={
                'class': 'form-select category-select',
                'size': 6
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-select tag-select',
                'size': 6
            }),
            'states': forms.SelectMultiple(attrs={
                'class': 'form-select state-select',
                'size': 6
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
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
    
