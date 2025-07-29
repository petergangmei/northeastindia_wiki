from django import template
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import escape
from urllib.parse import quote_plus
import re

register = template.Library()


@register.simple_tag(takes_context=True)
def get_social_image(context, article=None, content_type=None):
    """
    Get the appropriate social media image with fallbacks.
    Priority: Article featured image > Content type specific image > Default OG image
    """
    request = context['request']
    
    # If article has featured image, use it
    if article and hasattr(article, 'featured_image') and article.featured_image:
        if hasattr(article.featured_image, 'url') and article.featured_image.url:
            return request.build_absolute_uri(article.featured_image.url)
    
    # Content type specific fallback images
    fallback_images = {
        'person': 'images/person-placeholder.jpg',
        'place': 'images/place-placeholder.jpg',
        'culture': 'images/culture-placeholder.jpg',
        'event': 'images/event-placeholder.jpg',
        'festival': 'images/festival-placeholder.jpg',
        'art': 'images/art-placeholder.jpg',
    }
    
    # Use content type specific image if available
    if content_type and content_type.lower() in fallback_images:
        try:
            return request.build_absolute_uri(staticfiles_storage.url(fallback_images[content_type.lower()]))
        except:
            pass
    
    # Default fallback
    return request.build_absolute_uri(staticfiles_storage.url('images/default-og-image.jpg'))


@register.simple_tag
def get_social_description(title, excerpt=None, categories=None, states=None, max_length=155):
    """
    Generate optimized social media description with Northeast India context.
    """
    # Start with excerpt or generate from title
    if excerpt:
        base_description = excerpt.strip()
    else:
        base_description = f"Learn about {title}"
    
    # Add regional context
    regional_context = ""
    if states:
        if isinstance(states, str):
            regional_context = f" from {states}"
        else:
            try:
                state_list = list(states)[:2]  # Limit to 2 states
                if len(state_list) == 1:
                    regional_context = f" from {state_list[0].name}"
                elif len(state_list) == 2:
                    regional_context = f" from {state_list[0].name} and {state_list[1].name}"
                else:
                    regional_context = " from Northeast India"
            except:
                regional_context = " in Northeast India"
    else:
        regional_context = " in Northeast India"
    
    # Add cultural context
    cultural_suffix = " - Discover Seven Sisters states heritage"
    
    # Build full description
    full_description = f"{base_description}{regional_context}{cultural_suffix}"
    
    # Truncate if too long
    if len(full_description) > max_length:
        # Try without cultural suffix
        without_suffix = f"{base_description}{regional_context}"
        if len(without_suffix) <= max_length:
            full_description = without_suffix
        else:
            # Truncate base description
            available_length = max_length - len(regional_context) - 3  # 3 for "..."
            if available_length > 20:  # Ensure minimum meaningful length
                full_description = f"{base_description[:available_length]}...{regional_context}"
            else:
                full_description = base_description[:max_length-3] + "..."
    
    return full_description


@register.simple_tag
def get_social_keywords(title, categories=None, states=None, tags=None):
    """
    Generate comprehensive keywords for social media and SEO.
    """
    keywords = ['Northeast India', 'Seven Sisters states']
    
    # Add important words from title
    title_words = [word.strip() for word in title.split() if len(word) > 3 and word.lower() not in ['the', 'and', 'for', 'with']]
    keywords.extend(title_words[:3])
    
    # Add states
    if states:
        try:
            keywords.extend([state.name for state in states])
        except:
            if isinstance(states, str):
                keywords.append(states)
    
    # Add categories
    if categories:
        try:
            keywords.extend([cat.name for cat in categories])
        except:
            if isinstance(categories, str):
                keywords.append(categories)
    
    # Add tags (limit to avoid keyword stuffing)
    if tags:
        try:
            keywords.extend([tag.name for tag in tags[:5]])
        except:
            pass
    
    # Add cultural terms
    cultural_terms = ['culture', 'heritage', 'traditions', 'tribal culture', 'indigenous']
    keywords.extend(cultural_terms[:2])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword.lower() not in seen:
            seen.add(keyword.lower())
            unique_keywords.append(keyword)
    
    return ', '.join(unique_keywords)


@register.simple_tag
def get_twitter_creator(article=None):
    """
    Get Twitter creator handle for the article author.
    """
    if article and hasattr(article, 'author'):
        try:
            profile = article.author.profile
            if profile.twitter_handle:
                return f"@{profile.twitter_handle}"
        except:
            pass
    
    return "@NeIndiaWiki"  # Default site Twitter


@register.simple_tag
def get_article_type_schema(article):
    """
    Determine the schema.org type based on article content.
    """
    if not article:
        return "Article"
    
    title_lower = article.title.lower()
    content_lower = getattr(article, 'content', '').lower()
    
    # Check for person indicators
    person_indicators = ['born', 'died', 'biography', 'life', 'activist', 'leader', 'artist', 'musician', 'writer']
    if any(indicator in title_lower or indicator in content_lower for indicator in person_indicators):
        return "Person"
    
    # Check for place indicators
    place_indicators = ['temple', 'palace', 'monument', 'bridge', 'village', 'town', 'city', 'hill', 'river']
    if any(indicator in title_lower for indicator in place_indicators):
        return "Place"
    
    # Check for event indicators
    event_indicators = ['festival', 'celebration', 'ceremony', 'dance', 'music festival', 'fair']
    if any(indicator in title_lower for indicator in event_indicators):
        return "Event"
    
    return "Article"


@register.inclusion_tag('widgets/social_sharing_buttons.html', takes_context=True)
def social_sharing_buttons(context, article=None, title=None, url=None):
    """
    Render social sharing buttons with pre-filled content.
    """
    request = context['request']
    
    # Get data for sharing
    share_title = title or (article.title if article else "Northeast India Wiki")
    share_url = url or request.build_absolute_uri()
    
    # Generate description for sharing
    if article:
        share_description = get_social_description(
            article.title,
            getattr(article, 'excerpt', None),
            getattr(article, 'categories', None),
            getattr(article, 'states', None),
            max_length=200
        )
    else:
        share_description = "Discover the rich cultural heritage of Northeast India's Seven Sisters states"
    
    # URL encode for sharing
    encoded_title = quote_plus(share_title)
    encoded_url = quote_plus(share_url)
    encoded_description = quote_plus(share_description)
    
    # Create sharing URLs
    twitter_url = f"https://twitter.com/intent/tweet?text={encoded_title}&url={encoded_url}&hashtags=NortheastIndia,SevenSisters"
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}&quote={encoded_title}"
    linkedin_url = f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}&title={encoded_title}&summary={encoded_description}"
    whatsapp_url = f"https://wa.me/?text={encoded_title}%20{encoded_url}"
    
    return {
        'share_title': share_title,
        'share_url': share_url,
        'share_description': share_description,
        'twitter_url': twitter_url,
        'facebook_url': facebook_url,
        'linkedin_url': linkedin_url,
        'whatsapp_url': whatsapp_url,
    }


@register.simple_tag
def get_cultural_hashtags(article=None, states=None, categories=None):
    """
    Generate relevant hashtags for Northeast India content.
    """
    hashtags = ['#NortheastIndia', '#SevenSisters']
    
    # Add state-specific hashtags
    if states:
        try:
            for state in states[:2]:  # Limit to 2 states
                hashtag = f"#{state.name.replace(' ', '')}"
                hashtags.append(hashtag)
        except:
            pass
    
    # Add category-specific hashtags
    if categories:
        try:
            for category in categories[:2]:
                hashtag = f"#{category.name.replace(' ', '')}"
                hashtags.append(hashtag)
        except:
            pass
    
    # Add cultural hashtags
    cultural_tags = ['#Culture', '#Heritage', '#Traditions', '#Indigenous', '#TribalCulture']
    hashtags.extend(cultural_tags[:2])
    
    return ','.join([tag.replace('#', '') for tag in hashtags])


@register.filter
def truncate_social_text(text, max_length=280):
    """
    Truncate text for social media with proper word boundaries.
    """
    if not text or len(text) <= max_length:
        return text
    
    # Find the last space before max_length
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If we're not losing too much
        return text[:last_space] + "..."
    else:
        return text[:max_length-3] + "..."


@register.simple_tag(takes_context=True)
def structured_data_image(context, article=None):
    """
    Get properly structured image data for schema.org.
    """
    request = context['request']
    image_url = get_social_image(context, article)
    
    return {
        "@type": "ImageObject",
        "url": image_url,
        "width": 1200,
        "height": 630,
        "caption": article.title if article else "Northeast India Wiki",
        "contentLocation": {
            "@type": "Place",
            "name": "Northeast India",
            "addressRegion": "Northeast India",
            "addressCountry": "India"
        }
    }