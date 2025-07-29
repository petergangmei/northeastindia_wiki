"""
XML Sitemaps for Northeast India Wiki

This module provides comprehensive XML sitemaps for all content types in the wiki,
helping search engines efficiently discover and index Northeast India cultural content.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from .models import Article, Category, Tag, State


class StaticViewSitemap(Sitemap):
    """
    Sitemap for static pages and main site sections
    """
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        """Return list of static URL names"""
        return [
            'app:home',
            'app:article-list', 
            'app:categories',
            'app:article-tags',
            'app:article-search',
            # SEO-optimized landing pages
            'app:personalities-landing',
            'app:culture-landing', 
            'app:festivals-landing',
            'app:places-landing',
            'app:heritage-landing',
            # Regional pages
            'app:northeast-overview',
            'app:seven-sisters',
            'app:northeast-culture',
            'app:northeast-heritage',
            'app:state-list',
        ]

    def location(self, item):
        """Get the URL for each static page"""
        return reverse(item)

    def lastmod(self, item):
        """Return last modification date - use current time for dynamic pages"""
        return timezone.now()


class ArticleSitemap(Sitemap):
    """
    Sitemap for published articles - highest priority content
    
    Only includes published articles that have been approved to ensure
    search engines only index quality, reviewed content.
    """
    priority = 1.0
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        """Return published and approved articles"""
        return Article.objects.filter(
            published=True,
            review_status__in=['approved', 'featured']
        ).select_related('author').order_by('-published_at')

    def lastmod(self, obj):
        """Return the last modification time"""
        return obj.updated_at

    def location(self, obj):
        """Get the article URL"""
        return obj.get_absolute_url()

    def priority(self, obj):
        """Set priority based on article status"""
        if obj.review_status == 'featured':
            return 1.0
        return 0.9


class CategorySitemap(Sitemap):
    """
    Sitemap for article categories
    
    Categories help organize Northeast India content by topics like
    culture, history, personalities, etc.
    """
    priority = 0.7
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        """Return all categories that have published articles"""
        return Category.objects.filter(
            article_items__published=True,
            article_items__review_status__in=['approved', 'featured']
        ).distinct().order_by('name')

    def lastmod(self, obj):
        """Return the most recent update time of articles in this category"""
        latest_article = obj.article_items.filter(
            published=True,
            review_status__in=['approved', 'featured']
        ).order_by('-updated_at').first()
        
        if latest_article:
            return latest_article.updated_at
        return obj.updated_at

    def location(self, obj):
        """Get the category URL"""
        return reverse('app:article-category', kwargs={'slug': obj.slug})

    def priority(self, obj):
        """Set priority based on number of articles in category"""
        article_count = obj.article_items.filter(
            published=True,
            review_status__in=['approved', 'featured']
        ).count()
        
        if article_count >= 10:
            return 0.8
        elif article_count >= 5:
            return 0.7
        return 0.6


class TagSitemap(Sitemap):
    """
    Sitemap for article tags
    
    Tags provide granular labeling for specific topics, places,
    and themes within Northeast India content.
    """
    priority = 0.6
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        """Return tags that are used by published articles"""
        return Tag.objects.filter(
            article_items__published=True,
            article_items__review_status__in=['approved', 'featured']
        ).distinct().order_by('name')

    def lastmod(self, obj):
        """Return the most recent update time of articles with this tag"""
        latest_article = obj.article_items.filter(
            published=True,
            review_status__in=['approved', 'featured']
        ).order_by('-updated_at').first()
        
        if latest_article:
            return latest_article.updated_at
        return obj.updated_at

    def location(self, obj):
        """Get the tag URL"""
        return reverse('app:article-tag', kwargs={'slug': obj.slug})

    def priority(self, obj):
        """Set priority based on number of articles with this tag"""
        article_count = obj.article_items.filter(
            published=True,
            review_status__in=['approved', 'featured']
        ).count()
        
        if article_count >= 5:
            return 0.7
        elif article_count >= 2:
            return 0.6
        return 0.5


class PersonalitySitemap(Sitemap):
    """
    Sitemap for personality profiles
    
    Covers notable personalities from Northeast India including
    leaders, artists, writers, and cultural figures.
    """
    priority = 0.8
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        """Return published personality profiles"""
        from .models import Personality
        return Personality.objects.filter(
            published=True,
            review_status__in=['approved', 'featured']
        ).order_by('-published_at')

    def lastmod(self, obj):
        """Return the last modification time"""
        return obj.updated_at

    def location(self, obj):
        """Get the personality URL"""
        return obj.get_absolute_url()

    def priority(self, obj):
        """Set priority based on personality status"""
        if obj.review_status == 'featured':
            return 0.9
        return 0.8


class CulturalElementSitemap(Sitemap):
    """
    Sitemap for cultural elements
    
    Covers festivals, traditions, art forms, crafts, cuisine,
    and other cultural aspects of Northeast India.
    """
    priority = 0.8
    changefreq = 'monthly'
    protocol = 'https'

    def items(self):
        """Return published cultural elements"""
        from .models import CulturalElement
        return CulturalElement.objects.filter(
            published=True,
            review_status__in=['approved', 'featured']
        ).order_by('-published_at')

    def lastmod(self, obj):
        """Return the last modification time"""
        return obj.updated_at

    def location(self, obj):
        """Get the cultural element URL"""
        return obj.get_absolute_url()

    def priority(self, obj):
        """Set priority based on element status and type"""
        if obj.review_status == 'featured':
            return 0.9
        # Higher priority for festivals and traditions
        if obj.element_type in ['festival', 'tradition']:
            return 0.85
        return 0.8


class StateSitemap(Sitemap):
    """
    Sitemap for Northeast Indian states
    
    Provides information about each of the eight states of Northeast India
    including their geography, culture, and key information.
    """
    priority = 0.7
    changefreq = 'quarterly'
    protocol = 'https'

    def items(self):
        """Return all Northeast Indian states"""
        return State.objects.all().order_by('name')

    def lastmod(self, obj):
        """Return the last modification time"""
        return obj.updated_at

    def location(self, obj):
        """Get the state URL"""
        return reverse('app:state-detail', kwargs={'state_slug': obj.slug})

    def priority(self, obj):
        """All states have equal priority"""
        return 0.7


class SEOCategorySitemap(Sitemap):
    """
    Sitemap for SEO-optimized category-state combinations
    
    Generates URLs for category pages organized by states for better SEO targeting
    """
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'
    
    def items(self):
        """Return category-state combinations that have published articles"""
        categories = ['personalities', 'culture', 'festivals', 'places', 'heritage', 'traditional-crafts']
        states = State.objects.all()
        combinations = []
        
        for category_slug in categories:
            try:
                category = Category.objects.get(slug=category_slug)
                for state in states:
                    # Check if this combination has published articles
                    article_count = Article.objects.filter(
                        categories=category,
                        states=state,
                        published=True,
                        review_status__in=['approved', 'featured']
                    ).count()
                    
                    if article_count > 0:
                        combinations.append({
                            'category_slug': category_slug,
                            'state_slug': state.slug,
                            'state_name': state.name,
                            'category_name': category.name,
                            'article_count': article_count,
                            'last_updated': timezone.now()
                        })
            except Category.DoesNotExist:
                continue
                
        return combinations
    
    def location(self, obj):
        """Generate the SEO-optimized URL for category-state combination"""
        category_slug = obj['category_slug']
        state_slug = obj['state_slug']
        
        # Map to the appropriate URL pattern
        url_patterns = {
            'personalities': 'app:state-personalities',
            'culture': 'app:state-culture-articles',
            'festivals': 'app:state-festivals-articles',
            'places': 'app:state-places-articles',
            'heritage': 'app:state-heritage-articles',
            'traditional-crafts': 'app:state-crafts-articles',
        }
        
        url_name = url_patterns.get(category_slug)
        if url_name:
            return reverse(url_name, kwargs={'state_slug': state_slug})
        
        # Fallback to generic pattern
        return f"/{category_slug}/{state_slug}/"
    
    def lastmod(self, obj):
        """Return last modification time based on most recent article"""
        return obj['last_updated']
    
    def priority(self, obj):
        """Set priority based on number of articles"""
        article_count = obj['article_count']
        if article_count >= 10:
            return 0.9
        elif article_count >= 5:
            return 0.8
        return 0.7


# Sitemap registry for the sitemap index
SITEMAPS = {
    'static': StaticViewSitemap,
    'articles': ArticleSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'states': StateSitemap,
    'seo-categories': SEOCategorySitemap,
    # Note: Personality and CulturalElement sitemaps are commented out
    # until their corresponding views and URL patterns are implemented
    # 'personalities': PersonalitySitemap,
    # 'cultural-elements': CulturalElementSitemap,
}