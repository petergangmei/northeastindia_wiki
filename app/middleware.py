"""
SEO redirect middleware for Northeast India Wiki
Handles automatic redirects from old URL structure to new SEO-optimized URLs
"""
from django.shortcuts import redirect, get_object_or_404
from django.urls import resolve, Resolver404
from django.http import Http404
from .models import Content
import re


class SEORedirectMiddleware:
    """
    Middleware to handle automatic redirects from old URLs to new SEO-optimized URLs
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Compile regex patterns for performance
        self.old_article_pattern = re.compile(r'^/articles/([^/]+)/?$')
        self.old_category_pattern = re.compile(r'^/categories/([^/]+)/?$')
        
    def __call__(self, request):
        # Check if this is an old-style URL that needs redirecting
        redirect_response = self.check_for_redirect(request)
        if redirect_response:
            return redirect_response
            
        response = self.get_response(request)
        return response
    
    def check_for_redirect(self, request):
        """
        Check if the current request should be redirected to a new SEO URL
        """
        path = request.path
        
        # Handle old article URLs: /articles/slug/ -> new SEO URL
        article_match = self.old_article_pattern.match(path)
        if article_match:
            slug = article_match.group(1)
            return self.redirect_article(request, slug)
        
        # Handle old category URLs: /categories/slug/ -> new category structure
        category_match = self.old_category_pattern.match(path)
        if category_match:
            category_slug = category_match.group(1)
            return self.redirect_category(request, category_slug)
        
        return None
    
    def redirect_article(self, request, slug):
        """
        Redirect old article URL to new SEO-optimized URL
        """
        try:
            article = Content.objects.select_related().prefetch_related(
                'categories', 'states'
            ).get(slug=slug, published=True, content_type='article')
            
            # Get the SEO-optimized URL
            seo_url = article.get_absolute_url()
            
            # Only redirect if the new URL is different from current
            if seo_url != request.path:
                # Preserve query parameters
                if request.GET:
                    query_string = request.GET.urlencode()
                    seo_url += f'?{query_string}'
                
                return redirect(seo_url, permanent=True)
                
        except Content.DoesNotExist:
            # Article doesn't exist, let Django handle the 404
            pass
        except Exception:
            # Any other error, let the request continue normally
            pass
        
        return None
    
    def redirect_category(self, request, category_slug):
        """
        Redirect old category URLs to new category structure
        """
        # Map old category slugs to new URL patterns
        category_redirects = {
            'personalities': '/personalities/',
            'culture': '/culture/',
            'festivals': '/festivals/',
            'places': '/places/',
            'heritage': '/heritage/',
            'traditional-crafts': '/traditional-crafts/',
            'history': '/heritage/',  # Redirect history to heritage
            'food': '/culture/',      # Redirect food to culture
            'music': '/culture/',     # Redirect music to culture
            'dance': '/culture/',     # Redirect dance to culture
            'literature': '/culture/', # Redirect literature to culture
        }
        
        new_url = category_redirects.get(category_slug)
        if new_url and new_url != request.path:
            # Preserve query parameters
            if request.GET:
                query_string = request.GET.urlencode()
                new_url += f'?{query_string}'
            
            return redirect(new_url, permanent=True)
        
        return None


class CanonicalURLMiddleware:
    """
    Middleware to add canonical URL headers and handle URL normalization
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add canonical URL to response context for templates
        if hasattr(request, 'resolver_match') and request.resolver_match:
            try:
                # Try to determine canonical URL based on current view
                canonical_url = self.get_canonical_url(request)
                if canonical_url:
                    # Store canonical URL in request for template use
                    request.canonical_url = canonical_url
            except Exception:
                # Don't break the response if canonical URL generation fails
                pass
        
        return response
    
    def get_canonical_url(self, request):
        """
        Generate canonical URL for the current request
        """
        # Build the canonical URL
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        path = request.path
        
        # Remove trailing slash for consistency (except for root)
        if len(path) > 1 and path.endswith('/'):
            path = path[:-1]
        
        return f"{scheme}://{host}{path}"