import os
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.conf import settings


def smart_compress_image(image_file, max_width=1200, target_size_kb=100):
    """
    Intelligently compresses an image, choosing the best format and quality.
    Compares WebP and JPEG compression and returns the smaller file.
    
    Args:
        image_file: Django uploaded file or file-like object
        max_width: Maximum width in pixels (default 1200)
        target_size_kb: Target file size in KB (default 100)
    
    Returns:
        tuple: (ContentFile, filename_extension, original_size_kb, compressed_size_kb)
    """
    try:
        # Get original file size
        if hasattr(image_file, 'seek'):
            image_file.seek(0, 2)  # Seek to end
            original_size = image_file.tell()
            image_file.seek(0)  # Reset to beginning
        else:
            original_size = len(image_file.read())
            image_file.seek(0)
        
        original_size_kb = original_size / 1024
        
        # Open and process the image
        with Image.open(image_file) as img:
            # Store original format info
            original_format = img.format
            has_transparency = img.mode in ('RGBA', 'LA', 'P') and 'transparency' in img.info
            
            # Auto-orient based on EXIF data
            img = ImageOps.exif_transpose(img)
            
            # Resize if necessary while maintaining aspect ratio
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Try different compression strategies
            best_result = None
            best_size = float('inf')
            best_extension = '.webp'
            
            # Strategy 1: WebP compression with progressive quality
            webp_result = _try_webp_compression(img, has_transparency, target_size_kb)
            if webp_result:
                webp_data, webp_size = webp_result
                if webp_size < best_size:
                    best_result = webp_data
                    best_size = webp_size
                    best_extension = '.webp'
            
            # Strategy 2: Optimized JPEG compression (if no transparency)
            if not has_transparency:
                jpeg_result = _try_jpeg_compression(img, target_size_kb)
                if jpeg_result:
                    jpeg_data, jpeg_size = jpeg_result
                    if jpeg_size < best_size:
                        best_result = jpeg_data
                        best_size = jpeg_size
                        best_extension = '.jpg'
            
            # Strategy 3: Fall back to original if compressed is larger
            if best_size >= original_size_kb * 0.95:  # Only compress if we save at least 5%
                image_file.seek(0)
                original_data = image_file.read()
                return (
                    ContentFile(original_data),
                    _get_extension_from_format(original_format),
                    original_size_kb,
                    original_size_kb
                )
            
            # Return the best compressed result
            if best_result:
                return (
                    ContentFile(best_result),
                    best_extension,
                    original_size_kb,
                    best_size
                )
            else:
                # Fallback to original
                image_file.seek(0)
                original_data = image_file.read()
                return (
                    ContentFile(original_data),
                    _get_extension_from_format(original_format),
                    original_size_kb,
                    original_size_kb
                )
                
    except Exception as e:
        # If compression fails, raise exception
        raise ValueError(f"Failed to compress image: {str(e)}")


def _try_webp_compression(img, has_transparency, target_size_kb):
    """Try WebP compression with progressive quality reduction."""
    # Convert image for WebP
    if has_transparency:
        # Keep transparency for WebP
        if img.mode == 'P':
            img = img.convert('RGBA')
        webp_img = img
    else:
        # Convert to RGB for better compression
        if img.mode != 'RGB':
            webp_img = img.convert('RGB')
        else:
            webp_img = img
    
    # Try different quality levels
    for quality in [75, 70, 65, 60, 55]:
        output = BytesIO()
        webp_img.save(
            output, 
            format='WEBP', 
            quality=quality, 
            optimize=True,
            method=6  # Best compression method
        )
        
        size_kb = len(output.getvalue()) / 1024
        
        if size_kb <= target_size_kb or quality == 55:
            return output.getvalue(), size_kb
    
    return None


def _try_jpeg_compression(img, target_size_kb):
    """Try JPEG compression with progressive quality reduction."""
    # Convert to RGB for JPEG
    if img.mode != 'RGB':
        jpeg_img = img.convert('RGB')
    else:
        jpeg_img = img
    
    # Try different quality levels
    for quality in [80, 75, 70, 65, 60]:
        output = BytesIO()
        jpeg_img.save(
            output, 
            format='JPEG', 
            quality=quality, 
            optimize=True,
            progressive=True
        )
        
        size_kb = len(output.getvalue()) / 1024
        
        if size_kb <= target_size_kb or quality == 60:
            return output.getvalue(), size_kb
    
    return None


def _get_extension_from_format(format_name):
    """Convert PIL format name to file extension."""
    format_map = {
        'JPEG': '.jpg',
        'PNG': '.png',
        'WEBP': '.webp',
        'GIF': '.gif',
        'BMP': '.bmp',
        'TIFF': '.tiff'
    }
    return format_map.get(format_name, '.jpg')


# Keep backward compatibility
def compress_image_to_webp(image_file, quality=75, max_width=1200):
    """
    Legacy function for backward compatibility.
    Now uses smart compression but returns WebP format.
    """
    result = smart_compress_image(image_file, max_width, target_size_kb=100)
    compressed_file, extension, orig_size, comp_size = result
    
    # If it's not WebP, convert it to WebP
    if extension != '.webp':
        image_file.seek(0)
        with Image.open(image_file) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            output = BytesIO()
            img.save(output, format='WEBP', quality=quality, optimize=True, method=6)
            return ContentFile(output.getvalue())
    
    return compressed_file


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