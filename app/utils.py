"""
Utility functions for Northeast India Wiki
"""
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from django.urls import reverse
from django.conf import settings


def get_canonical_url(request, path=None, ignore_params=None):
    """
    Generate a canonical URL for SEO purposes.
    
    Args:
        request: Django HttpRequest object
        path: Optional custom path (defaults to current request path)
        ignore_params: List of query parameters to ignore (e.g., UTM parameters, pagination)
    
    Returns:
        Absolute canonical URL as string
    """
    if ignore_params is None:
        # Common parameters that should be ignored for canonical URLs
        ignore_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'ref', 'referrer', 'source', 'fbclid', 'gclid', 'msclkid',
            'page',  # Pagination should not be in canonical
            'sort',  # Sorting parameters
            'order', 'orderby',
            'view',  # View type parameters
            'format',
            'limit', 'offset',  # Pagination parameters
            'debug', 'preview',  # Development parameters
        ]
    
    # Use custom path or current request path
    current_path = path or request.path
    
    # Parse current query parameters
    query_params = request.GET.copy()
    
    # Remove ignored parameters
    for param in ignore_params:
        query_params.pop(param, None)
    
    # Build the canonical URL
    scheme = 'https' if request.is_secure() else request.scheme
    host = request.get_host()
    
    # Clean query string
    clean_query = query_params.urlencode() if query_params else ''
    
    # Construct the canonical URL
    if clean_query:
        canonical_url = f"{scheme}://{host}{current_path}?{clean_query}"
    else:
        canonical_url = f"{scheme}://{host}{current_path}"
    
    return canonical_url


def get_article_canonical_url(request, article):
    """
    Generate canonical URL for article pages.
    
    Args:
        request: Django HttpRequest object
        article: Article model instance
    
    Returns:
        Canonical URL for the article
    """
    article_path = reverse('app:article-detail', kwargs={'slug': article.slug})
    return get_canonical_url(request, path=article_path, ignore_params=[
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'ref', 'referrer', 'source', 'fbclid', 'gclid', 'msclkid',
        'preview', 'debug', 'edit', 'revision'
    ])


def get_category_canonical_url(request, category, ignore_filters=True):
    """
    Generate canonical URL for category pages.
    
    Args:
        request: Django HttpRequest object
        category: Category model instance
        ignore_filters: Whether to ignore filter parameters (default: True for canonical)
    
    Returns:
        Canonical URL for the category
    """
    category_path = reverse('app:article-category', kwargs={'slug': category.slug})
    
    if ignore_filters:
        # For canonical URLs, ignore all filter parameters
        ignore_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'ref', 'referrer', 'source', 'fbclid', 'gclid', 'msclkid',
            'page', 'sort', 'order', 'orderby',
            'subcategory', 'tag', 'state', 'date_from', 'date_to',
            'author', 'search', 'q', 'view', 'format'
        ]
    else:
        # Keep some meaningful parameters but remove tracking ones
        ignore_params = [
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'ref', 'referrer', 'source', 'fbclid', 'gclid', 'msclkid',
            'page', 'debug', 'preview'
        ]
    
    return get_canonical_url(request, path=category_path, ignore_params=ignore_params)


def get_tag_canonical_url(request, tag):
    """
    Generate canonical URL for tag pages.
    
    Args:
        request: Django HttpRequest object
        tag: Tag model instance
    
    Returns:
        Canonical URL for the tag
    """
    tag_path = reverse('app:article-tag', kwargs={'slug': tag.slug})
    return get_canonical_url(request, path=tag_path, ignore_params=[
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'ref', 'referrer', 'source', 'fbclid', 'gclid', 'msclkid',
        'page', 'sort', 'order', 'orderby', 'view', 'format'
    ])


def get_home_canonical_url(request):
    """
    Generate canonical URL for home page.
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        Canonical URL for the home page
    """
    home_path = reverse('app:home')
    return get_canonical_url(request, path=home_path, ignore_params=[
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'ref', 'referrer', 'source', 'fbclid', 'gclid', 'msclkid',
        'search', 'q', 'preview', 'debug'
    ])


def get_search_canonical_url(request):
    """
    Generate canonical URL for search pages.
    For search pages, we keep the 'q' parameter as it's essential for the content.
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        Canonical URL for the search
    """
    search_path = reverse('app:article-search')
    return get_canonical_url(request, path=search_path, ignore_params=[
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'ref', 'referrer', 'source', 'fbclid', 'gclid', 'msclkid',
        'page', 'sort', 'order', 'orderby', 'view', 'format', 'debug'
    ])


def normalize_url_for_canonical(url):
    """
    Normalize a URL for canonical purposes by removing unnecessary parameters
    and ensuring consistent formatting.
    
    Args:
        url: URL string to normalize
    
    Returns:
        Normalized URL string
    """
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query, keep_blank_values=False)
    
    # Remove tracking and session parameters
    ignore_params = [
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'ref', 'referrer', 'source', 'fbclid', 'gclid', 'msclkid',
        'sessionid', 'jsessionid', 'phpsessid',
        'timestamp', '_t', 'cache', 'v', 'version'
    ]
    
    # Filter out ignored parameters
    clean_params = {k: v for k, v in query_params.items() if k not in ignore_params}
    
    # Rebuild query string
    clean_query = urlencode(clean_params, doseq=True) if clean_params else ''
    
    # Reconstruct URL
    clean_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        clean_query,
        ''  # Remove fragment for canonical URLs
    ))
    
    return clean_url


def is_secure_connection(request):
    """
    Check if the current request is using a secure connection.
    This is useful for ensuring canonical URLs use the correct protocol.
    
    Args:
        request: Django HttpRequest object
    
    Returns:
        Boolean indicating if connection is secure
    """
    return request.is_secure() or (
        hasattr(settings, 'SECURE_PROXY_SSL_HEADER') and
        settings.SECURE_PROXY_SSL_HEADER and
        request.META.get(settings.SECURE_PROXY_SSL_HEADER[0]) == settings.SECURE_PROXY_SSL_HEADER[1]
    )


def get_enhanced_related_articles(article, limit=6):
    """
    Get related articles using a sophisticated algorithm that prioritizes:
    1. Articles from the same state(s)  
    2. Articles of the same content type (Person, Cultural, Event, Place)
    3. Articles sharing categories
    4. Articles sharing tags
    5. Regional connections (Northeast India focus)
    
    Returns articles with scores for better relevance ranking.
    """
    from .models import Article
    from .templatetags.schema_tags import detect_content_type
    
    if not article.published or article.review_status != 'approved':
        return []
    
    # Get base queryset of published, approved articles excluding current article
    base_queryset = Article.objects.filter(
        published=True, 
        review_status='approved'
    ).exclude(id=article.id)
    
    # Get article metadata for scoring
    article_states = list(article.states.all())
    article_categories = list(article.categories.all())
    article_tags = list(article.tags.all())
    article_content_type = detect_content_type(article)
    
    scored_articles = []
    
    # Evaluate each potential related article
    for candidate in base_queryset.select_related('author').prefetch_related(
        'states', 'categories', 'tags'
    ):
        score = 0
        reasons = []
        
        # 1. Same state bonus (highest priority for Northeast India wiki)
        candidate_states = list(candidate.states.all())
        shared_states = set(s.id for s in article_states) & set(s.id for s in candidate_states)
        if shared_states:
            state_score = len(shared_states) * 50  # High score for state matches
            score += state_score
            state_names = [s.name for s in article_states if s.id in shared_states]
            reasons.append(f"Same region: {', '.join(state_names)}")
        
        # 2. Same content type bonus (connects personalities to personalities, etc.)
        candidate_content_type = detect_content_type(candidate)
        if candidate_content_type == article_content_type and candidate_content_type != 'Article':
            score += 30
            reasons.append(f"Same type: {candidate_content_type}")
        
        # 3. Shared categories (strong thematic connection)
        candidate_categories = list(candidate.categories.all())
        shared_categories = set(c.id for c in article_categories) & set(c.id for c in candidate_categories)
        if shared_categories:
            category_score = len(shared_categories) * 20
            score += category_score
            category_names = [c.name for c in article_categories if c.id in shared_categories]
            reasons.append(f"Similar topics: {', '.join(category_names)}")
        
        # 4. Shared tags (moderate thematic connection)
        candidate_tags = list(candidate.tags.all())
        shared_tags = set(t.id for t in article_tags) & set(t.id for t in candidate_tags)
        if shared_tags:
            tag_score = len(shared_tags) * 10
            score += tag_score
            if len(shared_tags) <= 3:  # Only show tag names if not too many
                tag_names = [t.name for t in article_tags if t.id in shared_tags]
                reasons.append(f"Related: {', '.join(tag_names)}")
        
        # 5. Special Northeast India content bonuses
        score += _calculate_regional_connection_bonus(article, candidate)
        
        # 6. Recency bonus (slight preference for newer content)
        import datetime
        if candidate.published_at and candidate.published_at > (
            datetime.datetime.now() - datetime.timedelta(days=365)
        ).replace(tzinfo=candidate.published_at.tzinfo):
            score += 5
            reasons.append("Recent")
        
        # Only include articles with meaningful connections
        if score > 0:
            scored_articles.append({
                'article': candidate,
                'score': score,
                'reasons': reasons,
                'shared_states': len(shared_states) if shared_states else 0,
                'content_type_match': candidate_content_type == article_content_type
            })
    
    # Sort by score (highest first), then by publication date for ties
    scored_articles.sort(key=lambda x: (-x['score'], -x['article'].published_at.timestamp() if x['article'].published_at else 0))
    
    # Return top articles, ensuring diversity
    return _ensure_related_articles_diversity(scored_articles, limit)


def _calculate_regional_connection_bonus(article, candidate):
    """
    Calculate bonus points for regional connections specific to Northeast India.
    """
    from .templatetags.schema_tags import detect_content_type
    
    bonus = 0
    
    # Personality to cultural/event connections
    article_type = detect_content_type(article)
    candidate_type = detect_content_type(candidate)
    
    # Cross-type connections that make sense for Northeast India content
    meaningful_connections = {
        ('Person', 'Cultural'): 15,  # Personalities connected to cultural practices
        ('Person', 'Event'): 12,     # Personalities connected to festivals/events  
        ('Cultural', 'Event'): 20,   # Cultural practices connected to festivals
        ('Place', 'Cultural'): 18,   # Places connected to cultural practices
        ('Place', 'Event'): 15,      # Places connected to festivals/events
        ('Event', 'Cultural'): 20,   # Events connected to cultural practices
    }
    
    connection_key = (article_type, candidate_type)
    reverse_key = (candidate_type, article_type)
    
    if connection_key in meaningful_connections:
        bonus += meaningful_connections[connection_key]
    elif reverse_key in meaningful_connections:
        bonus += meaningful_connections[reverse_key]
    
    return bonus


def _ensure_related_articles_diversity(scored_articles, limit):
    """
    Ensure diversity in the final selection of related articles.
    Prioritizes different content types and states for better user experience.
    """
    from .templatetags.schema_tags import detect_content_type
    if len(scored_articles) <= limit:
        return [item['article'] for item in scored_articles]
    
    final_articles = []
    used_content_types = set()
    used_states = set()
    
    # First pass: Pick highest scoring articles with unique content types and states
    for item in scored_articles:
        if len(final_articles) >= limit:
            break
            
        article = item['article']
        content_type = detect_content_type(article)
        article_states = set(s.id for s in article.states.all())
        
        # Prefer articles with unique content types or states (up to limit/2)
        if len(final_articles) < limit // 2:
            if (content_type not in used_content_types or 
                not article_states.intersection(used_states)):
                final_articles.append(article)
                used_content_types.add(content_type)
                used_states.update(article_states)
                continue
        
        # Second half: Add remaining highest-scoring articles regardless of diversity
        if len(final_articles) >= limit // 2:
            final_articles.append(article)
    
    # Fill remaining slots with top-scored articles if we're under the limit
    for item in scored_articles:
        if len(final_articles) >= limit:
            break
        if item['article'] not in final_articles:
            final_articles.append(item['article'])
    
    return final_articles[:limit]


def get_contextual_links_data(article):
    """
    Generate contextual linking data for use in templates.
    Returns structured data for different types of related content.
    """
    from .models import Article, Personality, CulturalElement, State
    from .templatetags.schema_tags import detect_content_type
    
    data = {
        'more_from_states': [],
        'related_personalities': [],
        'cultural_connections': [],
        'cross_category_suggestions': [],
        'seasonal_related': []
    }
    
    article_states = list(article.states.all())
    article_categories = list(article.categories.all())
    content_type = detect_content_type(article)
    
    # More from same states
    if article_states:
        for state in article_states[:2]:  # Limit to 2 states to avoid overwhelming
            state_articles = Article.objects.filter(
                states=state,
                published=True,
                review_status='approved'
            ).exclude(id=article.id).order_by('-published_at')[:4]
            
            if state_articles:
                data['more_from_states'].append({
                    'state': state,
                    'articles': state_articles
                })
    
    # Related personalities (if current article is not about a person)
    if content_type != 'Person' and article_states:
        state_ids = [s.id for s in article_states]
        related_personalities = Article.objects.filter(
            states__id__in=state_ids,
            published=True,
            review_status='approved'
        ).exclude(id=article.id)
        
        # Filter to likely personality articles
        personality_articles = []
        for art in related_personalities[:10]:  # Check top 10 for efficiency
            if detect_content_type(art) == 'Person':
                personality_articles.append(art)
                if len(personality_articles) >= 3:
                    break
        
        data['related_personalities'] = personality_articles
    
    # Cultural connections (festivals to traditions, arts to crafts, etc.)
    if content_type in ['Cultural', 'Event'] and article_categories:
        category_ids = [c.id for c in article_categories]
        cultural_articles = Article.objects.filter(
            categories__id__in=category_ids,
            published=True,
            review_status='approved'
        ).exclude(id=article.id)
        
        cultural_connections = []
        for art in cultural_articles[:8]:
            art_type = detect_content_type(art)
            if art_type in ['Cultural', 'Event'] and art_type != content_type:
                cultural_connections.append(art)
                if len(cultural_connections) >= 3:
                    break
        
        data['cultural_connections'] = cultural_connections
    
    return data


def get_discover_more_suggestions(context_type, context_object, limit=5):
    """
    Get discovery suggestions based on context (category page, tag page, etc.).
    Helps users discover related content they might not find otherwise.
    """
    from .models import Article, Category, Tag
    from .templatetags.schema_tags import detect_content_type
    
    suggestions = []
    
    if context_type == 'category':
        category = context_object
        
        # Find related categories (parent/child relationships)
        related_categories = []
        if category.parent:
            related_categories.append(category.parent)
            siblings = Category.objects.filter(parent=category.parent).exclude(id=category.id)[:3]
            related_categories.extend(siblings)
        else:
            children = Category.objects.filter(parent=category)[:4]
            related_categories.extend(children)
        
        for related_cat in related_categories:
            article_count = Article.objects.filter(
                categories=related_cat,
                published=True,
                review_status='approved'
            ).count()
            if article_count > 0:
                suggestions.append({
                    'type': 'category',
                    'object': related_cat,
                    'article_count': article_count,
                    'reason': 'Related topic'
                })
    
    elif context_type == 'tag':
        tag = context_object
        
        # Find tags that co-occur with this tag
        articles_with_tag = Article.objects.filter(
            tags=tag,
            published=True,
            review_status='approved'
        )
        
        related_tags = Tag.objects.filter(
            article_items__in=articles_with_tag
        ).exclude(id=tag.id).distinct()[:limit]
        
        for related_tag in related_tags:
            article_count = Article.objects.filter(
                tags=related_tag,
                published=True,
                review_status='approved'
            ).count()
            suggestions.append({
                'type': 'tag',
                'object': related_tag,
                'article_count': article_count,
                'reason': 'Often mentioned together'
            })
    
    return suggestions[:limit]