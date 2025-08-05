from django import forms
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from tinymce.widgets import TinyMCE
from .models import Content, Category, Tag, State
import json

class InfoBoxDataWidget(forms.Widget):
    """
    Custom widget for handling dynamic label-value pairs for info box data
    """
    
    def format_value(self, value):
        """
        Convert the value from database into format suitable for widget rendering
        """
        # Handle None or empty values
        if value is None or value == '' or value == {}:
            return []
        
        # Handle dict (most common case from JSONField and form re-rendering)
        if isinstance(value, dict):
            # Don't try to JSON parse if it's already a dict
            if len(value) == 0:
                return []
            return [{'label': k, 'value': v} for k, v in value.items()]
        
        # Handle string that might be JSON (from initial form load)
        if isinstance(value, str):
            try:
                parsed_value = json.loads(value)
                if isinstance(parsed_value, dict):
                    if len(parsed_value) == 0:
                        return []
                    return [{'label': k, 'value': v} for k, v in parsed_value.items()]
            except (json.JSONDecodeError, TypeError):
                # If it's not valid JSON, treat as empty
                return []
        
        # Handle list format (in case it's already formatted)
        if isinstance(value, list):
            return value
        
        # Fallback for unexpected formats
        return []
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        widget_id = attrs.get('id', f'id_{name}')
        formatted_value = self.format_value(value)
        
        # Generate HTML directly
        html = f'''
        <div class="info-box-data-widget" id="{widget_id}_container">
            <label class="form-label">Info Box Data</label>
            <small class="form-text text-muted mb-3 d-block">Add label-value pairs that will appear in the info box (e.g., Name: Peter, Age: 25, Location: Meghalaya)</small>
            
            <div class="info-box-pairs" id="{widget_id}_pairs">
        '''
        
        # Add existing pairs or one empty pair
        if formatted_value:
            for pair in formatted_value:
                escaped_label = escape(pair['label'])
                escaped_value = escape(pair['value'])
                html += f'''
                <div class="info-box-pair row mb-2">
                    <div class="col-md-4">
                        <input type="text" 
                               name="{name}_label" 
                               value="{escaped_label}" 
                               placeholder="Label (e.g., Name)" 
                               class="form-control info-box-label">
                    </div>
                    <div class="col-md-6">
                        <input type="text" 
                               name="{name}_value" 
                               value="{escaped_value}" 
                               placeholder="Value (e.g., Peter)" 
                               class="form-control info-box-value">
                    </div>
                    <div class="col-md-2">
                        <button type="button" class="btn btn-outline-danger btn-sm remove-pair">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                '''
        else:
            # Default empty pair
            html += f'''
            <div class="info-box-pair row mb-2">
                <div class="col-md-4">
                    <input type="text" 
                           name="{name}_label" 
                           value="" 
                           placeholder="Label (e.g., Name)" 
                           class="form-control info-box-label">
                </div>
                <div class="col-md-6">
                    <input type="text" 
                           name="{name}_value" 
                           value="" 
                           placeholder="Value (e.g., Peter)" 
                           class="form-control info-box-value">
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-outline-danger btn-sm remove-pair">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            '''
        
        html += f'''
            </div>
            
            <div class="mt-3">
                <button type="button" class="btn btn-outline-primary btn-sm add-pair" data-target="{widget_id}_pairs" data-name="{name}">
                    <i class="fas fa-plus"></i> Add Field
                </button>
            </div>
            
            <!-- Hidden field to help with form processing -->
            <input type="hidden" name="{name}_count" id="{widget_id}_count" value="{len(formatted_value) if formatted_value else 1}">
        </div>
        '''
        
        return mark_safe(html)
    
    def value_from_datadict(self, data, files, name):
        labels = data.getlist(f'{name}_label')
        values = data.getlist(f'{name}_value')
        
        result = {}
        for label, value in zip(labels, values):
            if label.strip() and value.strip():  # Only include non-empty pairs
                result[label.strip()] = value.strip()
        
        return result
    
    class Media:
        js = ('js/info_box_widget.js',)
        css = {'all': ('css/info_box_widget.css',)}


class InfoBoxDataField(forms.JSONField):
    """
    Custom JSONField that properly handles empty values and dict data
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)
        self.widget = InfoBoxDataWidget()
    
    def bound_data(self, data, initial):
        """
        Override bound_data to prevent JSON parsing of dict data
        """
        if isinstance(data, dict):
            # If it's already a dict, don't try to parse it
            return data
        # For string data, use the parent's bound_data method
        return super().bound_data(data, initial)
    
    def to_python(self, value):
        if value is None or value == '' or value == {}:
            return {}
        if isinstance(value, dict):
            return value
        return super().to_python(value)
    
    def validate(self, value):
        # Allow empty dict
        if value == {} or value is None:
            return
        super().validate(value)


class ArticleForm(forms.ModelForm):
    """
    Form for creating and editing articles
    """
    info_box_data = InfoBoxDataField()
    
    content = forms.CharField(widget=TinyMCE(attrs={
        'cols': 80, 
        'rows': 30,
        'class': 'form-control'
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
            'states', 'featured_image', 'meta_description', 'content_type', 'info_box_data'
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
    
