from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from .utils.image_compression import compress_image_to_webp, get_webp_filename
import io


class CompressedImageField(models.ImageField):
    """
    Custom ImageField that automatically compresses uploaded images to WebP format.
    """
    
    def __init__(self, quality=85, max_width=1200, *args, **kwargs):
        self.quality = quality
        self.max_width = max_width
        super().__init__(*args, **kwargs)
    
    def save_form_data(self, instance, data):
        """
        Compress image data before saving to model instance.
        This method is called when form data is being saved to the model.
        """
        if data and hasattr(data, 'file') and data.file:
            try:
                # Compress the image
                compressed_file = compress_image_to_webp(
                    data.file, 
                    quality=self.quality, 
                    max_width=self.max_width
                )
                
                # Get the new WebP filename
                webp_name = get_webp_filename(data.name)
                
                # Read the compressed data once
                compressed_data = compressed_file.read()
                
                # Create a new InMemoryUploadedFile with compressed data
                compressed_upload = InMemoryUploadedFile(
                    file=io.BytesIO(compressed_data),
                    field_name=data.field_name if hasattr(data, 'field_name') else None,
                    name=webp_name,
                    content_type='image/webp',
                    size=len(compressed_data),
                    charset=None
                )
                
                # Replace the original file with compressed version
                data = compressed_upload
                
            except Exception as e:
                raise ValidationError(f"Image compression failed: {str(e)}")
        
        # Call parent method to handle the actual saving
        super().save_form_data(instance, data)
    
    def pre_save(self, model_instance, add):
        """
        Additional handling to ensure filename is correct before saving.
        """
        file = super().pre_save(model_instance, add)
        
        # If we have a file and it's not already a .webp, something went wrong
        if file and hasattr(file, 'name') and file.name:
            if not file.name.endswith('.webp'):
                # Try to fix the filename
                webp_name = get_webp_filename(file.name)
                file.name = webp_name
        
        return file
    
    def deconstruct(self):
        """
        Support for Django migrations.
        """
        name, path, args, kwargs = super().deconstruct()
        if self.quality != 85:
            kwargs['quality'] = self.quality
        if self.max_width != 1200:
            kwargs['max_width'] = self.max_width
        return name, path, args, kwargs