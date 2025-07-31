import os
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.conf import settings


def compress_image_to_webp(image_file, quality=85, max_width=1200):
    """
    Compresses an image to WebP format with specified quality and max width.
    
    Args:
        image_file: Django uploaded file or file-like object
        quality: WebP quality (1-100, default 85)
        max_width: Maximum width in pixels (default 1200)
    
    Returns:
        ContentFile: Compressed WebP image as Django ContentFile
    """
    try:
        # Ensure we can read from the beginning of the file
        if hasattr(image_file, 'seek'):
            image_file.seek(0)
            
        # Open and process the image
        with Image.open(image_file) as img:
            # Convert to RGB if necessary (WebP requires RGB)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Auto-orient based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Resize if necessary while maintaining aspect ratio
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save as WebP
            output = BytesIO()
            img.save(output, format='WEBP', quality=quality, optimize=True)
            output.seek(0)
            
            # Create ContentFile with the compressed data
            compressed_content = ContentFile(output.getvalue())
            
            return compressed_content
            
    except Exception as e:
        # If compression fails, raise exception
        raise ValueError(f"Failed to compress image: {str(e)}")


def get_webp_filename(original_filename):
    """
    Converts filename to WebP extension.
    
    Args:
        original_filename: Original filename with extension
        
    Returns:
        str: Filename with .webp extension
    """
    if not original_filename:
        return 'image.webp'
    
    name, _ = os.path.splitext(original_filename)
    return f"{name}.webp"