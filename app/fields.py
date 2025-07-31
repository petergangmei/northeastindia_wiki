from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from .utils.image_compression import smart_compress_image
import io
import os


class CompressedImageField(models.ImageField):
    """
    Custom ImageField that intelligently compresses uploaded images.
    Uses smart compression to choose the best format (WebP vs JPEG) and quality.
    """
    
    def __init__(self, max_width=1200, target_size_kb=100, *args, **kwargs):
        self.max_width = max_width
        self.target_size_kb = target_size_kb
        super().__init__(*args, **kwargs)
    
    def save_form_data(self, instance, data):
        """
        Intelligently compress image data before saving to model instance.
        This method is called when form data is being saved to the model.
        """
        if data and hasattr(data, 'file') and data.file:
            try:
                # Use smart compression
                compressed_file, best_extension, orig_size_kb, comp_size_kb = smart_compress_image(
                    data.file, 
                    max_width=self.max_width,
                    target_size_kb=self.target_size_kb
                )
                
                # Get the optimized filename with correct extension
                base_name = os.path.splitext(data.name)[0]
                optimized_name = f"{base_name}{best_extension}"
                
                # Read the compressed data
                compressed_data = compressed_file.read()
                
                # Determine content type
                content_type_map = {
                    '.webp': 'image/webp',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg', 
                    '.png': 'image/png'
                }
                content_type = content_type_map.get(best_extension, 'image/jpeg')
                
                # Create a new InMemoryUploadedFile with optimized data
                optimized_upload = InMemoryUploadedFile(
                    file=io.BytesIO(compressed_data),
                    field_name=data.field_name if hasattr(data, 'field_name') else None,
                    name=optimized_name,
                    content_type=content_type,
                    size=len(compressed_data),
                    charset=None
                )
                
                # Replace the original file with optimized version
                data = optimized_upload
                
                # Log compression results for debugging
                if hasattr(self, '_compression_log'):
                    self._compression_log = {
                        'original_size_kb': round(orig_size_kb, 2),
                        'compressed_size_kb': round(comp_size_kb, 2),
                        'compression_ratio': round((1 - comp_size_kb / orig_size_kb) * 100, 1) if orig_size_kb > 0 else 0,
                        'format': best_extension,
                    }
                
            except Exception as e:
                raise ValidationError(f"Image compression failed: {str(e)}")
        
        # Call parent method to handle the actual saving
        super().save_form_data(instance, data)
    
    def deconstruct(self):
        """
        Support for Django migrations.
        """
        name, path, args, kwargs = super().deconstruct()
        if self.max_width != 1200:
            kwargs['max_width'] = self.max_width
        if self.target_size_kb != 100:
            kwargs['target_size_kb'] = self.target_size_kb
        return name, path, args, kwargs