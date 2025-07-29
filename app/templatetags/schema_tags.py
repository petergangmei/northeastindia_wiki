from django import template
from django.utils.safestring import mark_safe
import json
import re
from ..utils import (
    get_canonical_url, get_article_canonical_url, get_category_canonical_url,
    get_tag_canonical_url, get_home_canonical_url, get_search_canonical_url
)

register = template.Library()

# Northeast India specific content type detection keywords
PERSON_KEYWORDS = [
    'biography', 'personality', 'leader', 'artist', 'writer', 'politician', 
    'musician', 'dancer', 'activist', 'freedom fighter', 'chief minister',
    'governor', 'poet', 'author', 'singer', 'actor', 'filmmaker'
]

PLACE_KEYWORDS = [
    'city', 'town', 'village', 'district', 'state', 'river', 'mountain',
    'hill', 'valley', 'lake', 'park', 'sanctuary', 'temple', 'monastery',
    'palace', 'fort', 'archaeological', 'tourist', 'destination', 'capital'
]

EVENT_KEYWORDS = [
    'festival', 'celebration', 'ceremony', 'tradition', 'ritual', 'dance',
    'music', 'cultural', 'harvest', 'spring', 'new year', 'religious',
    'tribal', 'community', 'annual', 'seasonal'
]

CULTURAL_KEYWORDS = [
    'art', 'craft', 'cuisine', 'food', 'dish', 'recipe', 'attire', 'dress',
    'costume', 'language', 'dialect', 'literature', 'folklore', 'legend',
    'tradition', 'custom', 'belief', 'practice', 'heritage'
]

@register.simple_tag
def detect_content_type(article):
    """
    Detect the primary content type of an article based on categories, tags, and content
    """
    title_lower = article.title.lower()
    content_lower = article.content.lower() if article.content else ''
    excerpt_lower = article.excerpt.lower() if article.excerpt else ''
    
    # Get categories and tags
    categories = [cat.name.lower() for cat in article.categories.all()]
    tags = [tag.name.lower() for tag in article.tags.all()]
    
    # Combine all text for analysis
    all_text = f"{title_lower} {content_lower} {excerpt_lower} {' '.join(categories)} {' '.join(tags)}"
    
    # Score each content type
    person_score = sum(1 for keyword in PERSON_KEYWORDS if keyword in all_text)
    place_score = sum(1 for keyword in PLACE_KEYWORDS if keyword in all_text)
    event_score = sum(1 for keyword in EVENT_KEYWORDS if keyword in all_text)
    cultural_score = sum(1 for keyword in CULTURAL_KEYWORDS if keyword in all_text)
    
    # Determine primary type
    scores = {
        'Person': person_score,
        'Place': place_score,
        'Event': event_score,
        'Cultural': cultural_score
    }
    
    max_score = max(scores.values())
    if max_score > 0:
        return max(scores, key=scores.get)
    
    return 'Article'  # Default type

@register.simple_tag
def is_person_article(article):
    """Check if article is about a person/personality"""
    return detect_content_type(article) == 'Person'

@register.simple_tag
def is_place_article(article):
    """Check if article is about a place/location"""
    return detect_content_type(article) == 'Place'

@register.simple_tag
def is_event_article(article):
    """Check if article is about an event/festival"""
    return detect_content_type(article) == 'Event'

@register.simple_tag
def is_cultural_article(article):
    """Check if article is about cultural elements"""
    return detect_content_type(article) == 'Cultural'

@register.simple_tag
def extract_person_data(article):
    """Extract person-specific data from article content"""
    content = article.content.lower() if article.content else ''
    
    # Basic birth/death date extraction (simple regex patterns)
    birth_pattern = r'born.*?(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}|\d{4})'
    death_pattern = r'died.*?(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}|\d{4})'
    
    birth_match = re.search(birth_pattern, content)
    death_match = re.search(death_pattern, content)
    
    return {
        'birthDate': birth_match.group(1) if birth_match else None,
        'deathDate': death_match.group(1) if death_match else None,
        'birthPlace': None,  # Would need more sophisticated extraction
        'occupation': None   # Would need more sophisticated extraction
    }

@register.simple_tag
def extract_place_data(article):
    """Extract place-specific data from article content"""
    states = list(article.states.all())
    
    return {
        'addressRegion': states[0].name if states else 'Northeast India',
        'addressCountry': 'India',
        'geo': {
            '@type': 'GeoCoordinates',
            'latitude': None,  # Would need to add coordinates to State model
            'longitude': None
        }
    }

@register.simple_tag
def extract_event_data(article):
    """Extract event-specific data from article content"""
    content = article.content.lower() if article.content else ''
    
    # Simple date extraction for events
    date_pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december)'
    month_match = re.search(date_pattern, content)
    
    return {
        'eventType': 'Festival' if 'festival' in content else 'CulturalEvent',
        'startDate': None,  # Would need more sophisticated extraction
        'endDate': None,
        'location': None
    }

@register.simple_tag
def generate_breadcrumb_data(page_type, request, **kwargs):
    """Generate breadcrumb data for different page types"""
    breadcrumbs = [
        {
            'name': 'Home',
            'url': f"{request.scheme}://{request.get_host()}/",
            'position': 1
        }
    ]
    
    if page_type == 'article':
        article = kwargs.get('article')
        breadcrumbs.append({
            'name': 'Articles',
            'url': f"{request.scheme}://{request.get_host()}/articles/",
            'position': 2
        })
        
        # Add category breadcrumb if exists
        categories = list(article.categories.all())
        if categories:
            breadcrumbs.append({
                'name': categories[0].name,
                'url': f"{request.scheme}://{request.get_host()}/categories/{categories[0].slug}/",
                'position': 3
            })
            breadcrumbs.append({
                'name': article.title,
                'url': request.build_absolute_uri(),
                'position': 4,
                'is_current': True
            })
        else:
            breadcrumbs.append({
                'name': article.title,
                'url': request.build_absolute_uri(),
                'position': 3,
                'is_current': True
            })
    
    elif page_type == 'category':
        category = kwargs.get('category')
        breadcrumbs.append({
            'name': 'Categories',
            'url': f"{request.scheme}://{request.get_host()}/categories/",
            'position': 2
        })
        breadcrumbs.append({
            'name': category.name,
            'url': request.build_absolute_uri(),
            'position': 3,
            'is_current': True
        })
    
    elif page_type == 'tag':
        tag = kwargs.get('tag')
        breadcrumbs.append({
            'name': 'Tags',
            'url': f"{request.scheme}://{request.get_host()}/tags/",
            'position': 2
        })
        breadcrumbs.append({
            'name': tag.name,
            'url': request.build_absolute_uri(),
            'position': 3,
            'is_current': True
        })
    
    elif page_type == 'profile':
        username = kwargs.get('username')
        breadcrumbs.append({
            'name': 'Profiles',
            'url': f"{request.scheme}://{request.get_host()}/profile/",
            'position': 2
        })
        breadcrumbs.append({
            'name': username,
            'url': request.build_absolute_uri(),
            'position': 3,
            'is_current': True
        })
    
    elif page_type == 'search':
        query = kwargs.get('query', '')
        breadcrumbs.append({
            'name': 'Articles',
            'url': f"{request.scheme}://{request.get_host()}/articles/",
            'position': 2
        })
        search_title = f'Search Results for "{query}"' if query else 'Search Results'
        breadcrumbs.append({
            'name': search_title,
            'url': request.build_absolute_uri(),
            'position': 3,
            'is_current': True
        })
    
    elif page_type == 'article_list':
        breadcrumbs.append({
            'name': 'Articles',
            'url': request.build_absolute_uri(),
            'position': 2,
            'is_current': True
        })
    
    elif page_type == 'category_list':
        breadcrumbs.append({
            'name': 'Categories',
            'url': request.build_absolute_uri(),
            'position': 2,
            'is_current': True
        })
    
    elif page_type == 'tag_list':
        breadcrumbs.append({
            'name': 'Tags',
            'url': request.build_absolute_uri(),
            'position': 2,
            'is_current': True
        })
    
    elif page_type == 'article_history':
        article = kwargs.get('article')
        breadcrumbs.append({
            'name': 'Articles',
            'url': f"{request.scheme}://{request.get_host()}/articles/",
            'position': 2
        })
        breadcrumbs.append({
            'name': article.title,
            'url': f"{request.scheme}://{request.get_host()}/articles/{article.slug}/",
            'position': 3
        })
        breadcrumbs.append({
            'name': 'History',
            'url': request.build_absolute_uri(),
            'position': 4,
            'is_current': True
        })
    
    elif page_type == 'article_edit':
        article = kwargs.get('article')
        breadcrumbs.append({
            'name': 'Articles',
            'url': f"{request.scheme}://{request.get_host()}/articles/",
            'position': 2
        })
        breadcrumbs.append({
            'name': article.title,
            'url': f"{request.scheme}://{request.get_host()}/articles/{article.slug}/",
            'position': 3
        })
        breadcrumbs.append({
            'name': 'Edit',
            'url': request.build_absolute_uri(),
            'position': 4,
            'is_current': True
        })
    
    elif page_type == 'review_queue':
        breadcrumbs.append({
            'name': 'Articles',
            'url': f"{request.scheme}://{request.get_host()}/articles/",
            'position': 2
        })
        breadcrumbs.append({
            'name': 'Review Queue',
            'url': request.build_absolute_uri(),
            'position': 3,
            'is_current': True
        })
    
    elif page_type == 'notifications':
        breadcrumbs.append({
            'name': 'Notifications',
            'url': request.build_absolute_uri(),
            'position': 2,
            'is_current': True
        })
    
    return breadcrumbs

@register.simple_tag
def generate_breadcrumb_schema(page_type, request, **kwargs):
    """Generate Schema.org BreadcrumbList structured data"""
    breadcrumb_data = generate_breadcrumb_data(page_type, request, **kwargs)
    
    schema_items = []
    for breadcrumb in breadcrumb_data:
        schema_items.append({
            '@type': 'ListItem',
            'position': breadcrumb['position'],
            'name': breadcrumb['name'],
            'item': breadcrumb['url']
        })
    
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': schema_items
    }

@register.simple_tag
def get_northeast_states():
    """Get the Seven Sisters states of Northeast India"""
    return [
        'Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 
        'Mizoram', 'Nagaland', 'Tripura', 'Sikkim'
    ]

@register.filter
def jsonify(value):
    """Convert Python object to JSON string"""
    return mark_safe(json.dumps(value, indent=2))

@register.simple_tag
def get_article_reading_time(article):
    """Calculate estimated reading time for an article"""
    if not article.content:
        return 0
    
    # Remove HTML tags for word count
    import re
    text = re.sub(r'<[^>]+>', '', article.content)
    word_count = len(text.split())
    
    # Average reading speed is 200-250 words per minute
    reading_time = max(1, round(word_count / 225))
    return reading_time

@register.simple_tag
def get_schema_type_for_content(article):
    """Get the most appropriate Schema.org type for the article content"""
    content_type = detect_content_type(article)
    
    schema_types = {
        'Person': ['Article', 'Person'],
        'Place': ['Article', 'Place', 'TouristDestination'],
        'Event': ['Article', 'Event', 'Festival'],
        'Cultural': ['Article', 'CreativeWork', 'VisualArtwork']
    }
    
    return schema_types.get(content_type, ['Article'])

@register.simple_tag  
def extract_geographical_info(article):
    """Extract geographical information from article content and relationships"""
    geo_info = {
        'region': 'Northeast India',
        'country': 'India',
        'states': [],
        'coordinates': {
            'lat': 26.2006,  # Central NE India coordinates
            'lng': 92.9376
        }
    }
    
    # Add specific states if mentioned
    for state in article.states.all():
        geo_info['states'].append({
            'name': state.name,
            'capital': state.capital,
            'description': state.description
        })
    
    return geo_info

@register.simple_tag
def get_cultural_context(article):
    """Extract cultural context and significance from article"""
    categories = [cat.name.lower() for cat in article.categories.all()]
    tags = [tag.name.lower() for tag in article.tags.all()]
    
    cultural_elements = []
    
    # Check for cultural categories and tags
    cultural_indicators = {
        'festivals': ['festival', 'celebration', 'ceremony'],
        'arts': ['art', 'craft', 'painting', 'sculpture'],
        'music': ['music', 'song', 'instrument', 'dance'],
        'traditions': ['tradition', 'custom', 'ritual', 'practice'],
        'cuisine': ['food', 'cuisine', 'dish', 'recipe'],
        'language': ['language', 'dialect', 'literature'],
        'attire': ['dress', 'costume', 'attire', 'clothing']
    }
    
    all_terms = categories + tags
    
    for category, keywords in cultural_indicators.items():
        if any(keyword in term for term in all_terms for keyword in keywords):
            cultural_elements.append(category)
    
    return cultural_elements

@register.simple_tag
def generate_content_keywords(article):
    """Generate comprehensive keywords for the article based on content analysis"""
    keywords = set()
    
    # Add basic Northeast India keywords
    keywords.update([
        'Northeast India',
        'Seven Sisters states', 
        'Northeast Indian culture',
        'Indian heritage',
        'Tribal culture',
        'Indigenous traditions'
    ])
    
    # Add state-specific keywords
    for state in article.states.all():
        keywords.add(state.name)
        keywords.add(f"{state.name} culture")
        if state.capital:
            keywords.add(state.capital)
    
    # Add category-based keywords
    for category in article.categories.all():
        keywords.add(category.name)
        keywords.add(f"Northeast India {category.name}")
    
    # Add tag-based keywords
    for tag in article.tags.all():
        keywords.add(tag.name)
    
    # Add content-type specific keywords
    content_type = detect_content_type(article)
    if content_type == 'Person':
        keywords.update(['Northeast India personality', 'Indian leader', 'cultural figure'])
    elif content_type == 'Place':
        keywords.update(['Northeast India tourism', 'tourist destination', 'travel guide'])
    elif content_type == 'Event':
        keywords.update(['Northeast India festival', 'cultural event', 'traditional celebration'])
    elif content_type == 'Cultural':
        keywords.update(['traditional art', 'cultural heritage', 'indigenous practice'])
    
    return sorted(list(keywords))

@register.simple_tag
def get_article_mentions(article):
    """Extract mentions of notable entities from article content"""
    mentions = {
        'people': [],
        'places': [],
        'organizations': [],
        'events': []
    }
    
    # This is a simplified implementation
    # In a production system, you might use NLP libraries for entity extraction
    content_lower = article.content.lower() if article.content else ''
    
    # Common Northeast India personalities (example)
    ne_personalities = [
        'bhupen hazarika', 'mary kom', 'irom sharmila', 'bishnu prasad rabha',
        'mamang dai', 'temsula ao', 'robin s sharma'
    ]
    
    # Common places in Northeast India
    ne_places = [
        'guwahati', 'shillong', 'imphal', 'kohima', 'aizawl', 'agartala',
        'itanagar', 'gangtok', 'kaziranga', 'cherrapunji', 'tawang'
    ]
    
    for person in ne_personalities:
        if person in content_lower:
            mentions['people'].append(person.title())
    
    for place in ne_places:
        if place in content_lower:
            mentions['places'].append(place.title())
    
    return mentions


# Canonical URL template tags
@register.simple_tag
def canonical_url(request, path=None, ignore_params=None):
    """Generate canonical URL for any page"""
    return get_canonical_url(request, path=path, ignore_params=ignore_params)


@register.simple_tag
def article_canonical_url(request, article):
    """Generate canonical URL for article pages"""
    return get_article_canonical_url(request, article)


@register.simple_tag
def category_canonical_url(request, category, ignore_filters=True):
    """Generate canonical URL for category pages"""
    return get_category_canonical_url(request, category, ignore_filters=ignore_filters)


@register.simple_tag
def tag_canonical_url(request, tag):
    """Generate canonical URL for tag pages"""
    return get_tag_canonical_url(request, tag)


@register.simple_tag
def home_canonical_url(request):
    """Generate canonical URL for home page"""
    return get_home_canonical_url(request)


@register.simple_tag
def search_canonical_url(request):
    """Generate canonical URL for search pages"""
    return get_search_canonical_url(request)


# Northeast India SEO Optimized Title Generation
@register.simple_tag
def get_optimized_article_title(article, context='detail'):
    """
    Generate SEO-optimized titles for articles with regional keywords
    Keeps titles under 60 characters for optimal SEO
    """
    content_type = detect_content_type(article)
    title = article.title
    
    # Get primary state if available
    primary_state = None
    states = list(article.states.all())
    if states:
        primary_state = states[0].name
    
    # Get primary category
    primary_category = None
    categories = list(article.categories.all())
    if categories:
        primary_category = categories[0].name
    
    # Function to create and truncate titles
    def make_title(base_title, max_length=60):
        if len(base_title) <= max_length:
            return base_title
        # Try truncating the original article title first
        truncated_title = truncate_title(title, max_length - (len(base_title) - len(title)))
        return base_title.replace(title, truncated_title)
    
    # Base title depending on content type and context
    if context == 'detail':
        if content_type == 'Person':
            if primary_state:
                # Format: "Name - [Profession] from State | NE India"
                profession = _extract_profession_from_content(article)
                if profession and len(f"{title} - {profession} from {primary_state}") <= 45:
                    return make_title(f"{title} - {profession} from {primary_state} | NE India")
                elif len(f"{title} - {primary_state} Personality") <= 50:
                    return make_title(f"{title} - {primary_state} Personality | NE India")
                else:
                    return make_title(f"{title} | Northeast India Personality")
            else:
                return make_title(f"{title} | Northeast India Personality")
                
        elif content_type == 'Event':
            if primary_state:
                if _is_festival_article(article):
                    if len(f"{title} - {primary_state} Festival") <= 45:
                        return make_title(f"{title} - {primary_state} Festival | NE India")
                    else:
                        return make_title(f"{title} | Northeast India Festival")
                else:
                    if len(f"{title} in {primary_state}") <= 45:
                        return make_title(f"{title} in {primary_state} | Northeast India")
                    else:
                        return make_title(f"{title} | Northeast India Event")
            else:
                return make_title(f"{title} | Northeast India Festival")
                
        elif content_type == 'Cultural':
            if primary_state:
                cultural_type = _get_cultural_type(article)
                if cultural_type and len(f"{title} - {primary_state} {cultural_type}") <= 45:
                    return make_title(f"{title} - {primary_state} {cultural_type} | NE India")
                elif len(f"{title} in {primary_state}") <= 45:
                    return make_title(f"{title} in {primary_state} | NE India Heritage")
                else:
                    return make_title(f"{title} | Northeast India Heritage")
            else:
                return make_title(f"{title} | Northeast India Heritage")
                
        elif content_type == 'Place':
            if primary_state:
                if len(f"{title}, {primary_state}") <= 45:
                    return make_title(f"{title}, {primary_state} | Seven Sisters Tourism")
                else:
                    return make_title(f"{title} | Northeast India Tourism")
            else:
                return make_title(f"{title} | Northeast India Tourism")
        
        else:  # Default Article
            if primary_state:
                if len(f"{title} - {primary_state}") <= 40:
                    return make_title(f"{title} - {primary_state} | Seven Sisters Wiki")
                else:
                    return make_title(f"{title} | Seven Sisters | NE India Wiki")
            else:
                return make_title(f"{title} | Seven Sisters | Northeast India Wiki")
    
    elif context == 'list':
        # Shorter titles for list views with more aggressive truncation
        if content_type == 'Person' and primary_state:
            if len(f"{title} ({primary_state})") <= 50:
                return make_title(f"{title} ({primary_state}) - NE India Personality", 58)
            else:
                return make_title(f"{title} - Northeast India Personality", 58)
        elif content_type == 'Event' and primary_state:
            if len(f"{title} - {primary_state}") <= 45:
                return make_title(f"{title} - {primary_state} Festival", 58)
            else:
                return make_title(f"{title} - Northeast India Festival", 58)
        elif primary_state and len(f"{title} - {primary_state}") <= 45:
            return make_title(f"{title} - {primary_state} | Northeast India", 58)
        else:
            return make_title(f"{title} | Northeast India", 58)
    
    # Fallback
    return make_title(f"{title} | Northeast India Wiki")


@register.simple_tag  
def get_optimized_category_title(category, article_count=None):
    """Generate SEO-optimized titles for category pages"""
    if article_count is not None:
        return f"{category.name} Articles ({article_count}) | Northeast India Wiki"
    else:
        return f"{category.name} | Seven Sisters Culture | Northeast India"


@register.simple_tag
def get_optimized_tag_title(tag, article_count=None):
    """Generate SEO-optimized titles for tag pages"""
    if article_count is not None:
        return f"'{tag.name}' Articles ({article_count}) | NE India Wiki"
    else:
        return f"'{tag.name}' | Northeast India Heritage & Culture"


@register.simple_tag
def get_optimized_home_title(featured_count=None):
    """Generate SEO-optimized title for home page"""
    if featured_count:
        return f"Northeast India Wiki - {featured_count} Articles on Seven Sisters"
    else:
        return "Northeast India Wiki - Seven Sisters Culture & Heritage"


@register.simple_tag
def get_optimized_search_title(query=None, result_count=None):
    """Generate SEO-optimized titles for search results"""
    if query and result_count is not None:
        if len(query) <= 30:
            return f"'{query}' Search - {result_count} Results | NE India Wiki"
        else:
            return f"Search Results ({result_count}) | Northeast India Wiki"
    elif query:
        if len(query) <= 35:
            return f"'{query}' | Northeast India Wiki Search"
        else:
            return "Search Results | Northeast India Wiki"
    else:
        return "Search | Northeast India Wiki - Seven Sisters States"


# Helper functions for title optimization
def _extract_profession_from_content(article):
    """Extract profession/occupation from article content"""
    content = article.content.lower() if article.content else ''
    title = article.title.lower()
    
    professions = {
        'politician': ['politician', 'chief minister', 'minister', 'mla', 'mp', 'leader'],
        'artist': ['artist', 'painter', 'sculptor'],
        'musician': ['musician', 'singer', 'composer'],
        'writer': ['writer', 'author', 'poet', 'novelist'],
        'actor': ['actor', 'actress', 'film'],
        'activist': ['activist', 'social worker'],
        'sportsperson': ['athlete', 'sports', 'player', 'boxer'],
        'freedom fighter': ['freedom fighter', 'revolutionary'],
        'educator': ['teacher', 'professor', 'educator']
    }
    
    combined_text = f"{title} {content}"
    
    for profession, keywords in professions.items():
        if any(keyword in combined_text for keyword in keywords):
            return profession.title()
    
    return None


def _is_festival_article(article):
    """Check if article is specifically about a festival"""
    festival_keywords = ['festival', 'celebration', 'fest', 'puja', 'bihu', 'hornbill']
    title_lower = article.title.lower()
    categories = [cat.name.lower() for cat in article.categories.all()]
    tags = [tag.name.lower() for tag in article.tags.all()]
    
    all_terms = [title_lower] + categories + tags
    
    return any(keyword in term for term in all_terms for keyword in festival_keywords)


def _get_cultural_type(article):
    """Get specific cultural element type"""
    cultural_types = {
        'Tradition': ['tradition', 'custom', 'ritual'],
        'Art': ['art', 'craft', 'handicraft', 'weaving'],
        'Cuisine': ['food', 'dish', 'cuisine', 'recipe'],
        'Dance': ['dance', 'dancing'],
        'Music': ['music', 'song', 'instrument'],
        'Attire': ['dress', 'costume', 'attire', 'clothing'],
        'Language': ['language', 'dialect']
    }
    
    title_lower = article.title.lower()
    categories = [cat.name.lower() for cat in article.categories.all()]
    tags = [tag.name.lower() for tag in article.tags.all()]
    
    all_terms = [title_lower] + categories + tags
    
    for cultural_type, keywords in cultural_types.items():
        if any(keyword in term for term in all_terms for keyword in keywords):
            return cultural_type
    
    return None


@register.filter
def truncate_title(title, max_length=60):
    """Truncate title to specified length while keeping it readable"""
    if len(title) <= max_length:
        return title
    
    # Try to truncate at word boundary
    truncated = title[:max_length].rsplit(' ', 1)[0]
    if len(truncated) >= max_length - 10:  # If we get a reasonable length
        return truncated + "..."
    else:
        # If word boundary truncation is too short, just cut and add ellipsis
        return title[:max_length-3] + "..."


# Contextual Internal Linking Template Tags

@register.simple_tag
def get_state_articles(state, exclude_article=None, limit=4):
    """Get articles from a specific state, excluding current article"""
    from ..models import Article
    
    articles = Article.objects.filter(
        states=state,
        published=True,
        review_status='approved'
    ).order_by('-published_at')
    
    if exclude_article:
        articles = articles.exclude(id=exclude_article.id)
    
    return articles[:limit]


@register.simple_tag 
def get_personality_articles_from_states(states, exclude_article=None, limit=3):
    """Get personality articles from specific states"""
    from ..models import Article
    
    if not states:
        return []
    
    state_ids = [s.id for s in states]
    articles = Article.objects.filter(
        states__id__in=state_ids,
        published=True,
        review_status='approved'
    ).exclude(id=exclude_article.id if exclude_article else None).distinct()
    
    # Filter to personality articles
    personality_articles = []
    for article in articles[:10]:  # Check top 10 for efficiency
        if detect_content_type(article) == 'Person':
            personality_articles.append(article)
            if len(personality_articles) >= limit:
                break
    
    return personality_articles


@register.simple_tag
def get_cultural_articles_by_category(categories, exclude_article=None, limit=3):
    """Get cultural/event articles from specific categories"""
    from ..models import Article
    
    if not categories:
        return []
    
    category_ids = [c.id for c in categories]
    articles = Article.objects.filter(
        categories__id__in=category_ids,
        published=True,
        review_status='approved'
    ).exclude(id=exclude_article.id if exclude_article else None).distinct()
    
    cultural_articles = []
    exclude_type = detect_content_type(exclude_article) if exclude_article else None
    
    for article in articles[:8]:
        content_type = detect_content_type(article)
        if content_type in ['Cultural', 'Event'] and content_type != exclude_type:
            cultural_articles.append(article)
            if len(cultural_articles) >= limit:
                break
    
    return cultural_articles


@register.simple_tag
def get_random_articles_by_type(content_type, exclude_article=None, limit=3):
    """Get random articles of a specific content type"""
    from ..models import Article
    
    articles = Article.objects.filter(
        published=True,
        review_status='approved'
    ).exclude(id=exclude_article.id if exclude_article else None).order_by('?')
    
    typed_articles = []
    for article in articles[:20]:  # Check top 20 random articles
        if detect_content_type(article) == content_type:
            typed_articles.append(article)
            if len(typed_articles) >= limit:
                break
    
    return typed_articles


@register.simple_tag
def suggest_related_categories(current_category, limit=4):
    """Suggest related categories based on hierarchy and co-occurrence"""
    from ..models import Category, Article
    
    suggestions = []
    
    # Add parent and sibling categories
    if current_category.parent:
        suggestions.append(current_category.parent)
        siblings = Category.objects.filter(
            parent=current_category.parent
        ).exclude(id=current_category.id)[:2]
        suggestions.extend(siblings)
    
    # Add child categories
    children = Category.objects.filter(parent=current_category)[:2]
    suggestions.extend(children)
    
    # Add article counts to suggestions
    final_suggestions = []
    for category in suggestions[:limit]:
        article_count = Article.objects.filter(
            categories=category,
            published=True,
            review_status='approved'
        ).count()
        if article_count > 0:
            final_suggestions.append({
                'category': category,
                'article_count': article_count,
                'relationship': _get_category_relationship(current_category, category)
            })
    
    return final_suggestions


@register.simple_tag
def suggest_related_tags(current_tag, limit=5):
    """Suggest tags that co-occur with the current tag"""
    from ..models import Tag, Article
    
    # Get articles that have the current tag
    articles_with_tag = Article.objects.filter(
        tags=current_tag,
        published=True,
        review_status='approved'
    )
    
    # Find other tags that appear in these articles
    related_tags = Tag.objects.filter(
        article_items__in=articles_with_tag
    ).exclude(id=current_tag.id).distinct()
    
    # Add article counts and co-occurrence info
    suggestions = []
    for tag in related_tags[:limit]:
        article_count = Article.objects.filter(
            tags=tag,
            published=True,
            review_status='approved'
        ).count()
        
        co_occurrence_count = Article.objects.filter(
            tags__in=[current_tag, tag],
            published=True,
            review_status='approved'
        ).distinct().count()
        
        suggestions.append({
            'tag': tag,
            'article_count': article_count,
            'co_occurrence_count': co_occurrence_count
        })
    
    # Sort by co-occurrence frequency
    suggestions.sort(key=lambda x: x['co_occurrence_count'], reverse=True)
    return suggestions


@register.simple_tag
def get_cross_state_connections(current_states, exclude_article=None, limit=4):
    """Get articles from other Northeast states for cross-regional discovery"""
    from ..models import State, Article
    
    if not current_states:
        return []
    
    current_state_ids = [s.id for s in current_states]
    
    # Get other Northeast states
    other_states = State.objects.exclude(id__in=current_state_ids)[:3]
    
    cross_connections = []
    for state in other_states:
        articles = Article.objects.filter(
            states=state,
            published=True,
            review_status='approved'
        ).exclude(id=exclude_article.id if exclude_article else None).order_by('-published_at')[:2]
        
        if articles:
            cross_connections.append({
                'state': state,
                'articles': articles
            })
    
    return cross_connections[:limit]


@register.simple_tag
def get_seasonal_content(current_month=None, limit=3):
    """Get seasonal content relevant to the current time or specified month"""
    from ..models import Article
    import datetime
    
    if not current_month:
        current_month = datetime.datetime.now().month
    
    # Define seasonal keywords by month
    seasonal_keywords = {
        1: ['winter', 'january', 'new year', 'makar sankranti'],  # January
        2: ['spring', 'february', 'saraswati puja'],  # February  
        3: ['holi', 'march', 'spring', 'bihu'],  # March
        4: ['april', 'rongali bihu', 'spring festival', 'new year'],  # April
        5: ['may', 'kali puja', 'buddha purnima'],  # May
        6: ['june', 'ambubachi', 'monsoon'],  # June
        7: ['july', 'monsoon', 'teej'],  # July
        8: ['august', 'independence', 'raksha bandhan'],  # August
        9: ['september', 'durga puja', 'autumn'],  # September
        10: ['october', 'durga puja', 'kali puja', 'diwali'],  # October
        11: ['november', 'diwali', 'kali puja', 'autumn'],  # November
        12: ['december', 'christmas', 'winter']  # December
    }
    
    keywords = seasonal_keywords.get(current_month, [])
    if not keywords:
        return []
    
    # Search for articles containing seasonal keywords
    from django.db.models import Q
    query = Q()
    for keyword in keywords:
        query |= Q(title__icontains=keyword) | Q(content__icontains=keyword) | Q(tags__name__icontains=keyword)
    
    seasonal_articles = Article.objects.filter(
        query,
        published=True,
        review_status='approved'
    ).distinct().order_by('-published_at')[:limit]
    
    return seasonal_articles


@register.filter
def add_internal_links(content, current_article=None):
    """
    Automatically add internal links to content for mentioned places, personalities, etc.
    This is a basic implementation - in production, you'd want more sophisticated NLP.
    """
    if not content:
        return content
    
    from ..models import Article, State
    import re
    
    # Get potential link targets
    states = State.objects.all()
    articles = Article.objects.filter(
        published=True,
        review_status='approved'
    ).exclude(id=current_article.id if current_article else None)[:50]  # Limit for performance
    
    linked_content = content
    
    # Add state links
    for state in states:
        pattern = r'\b' + re.escape(state.name) + r'\b'
        if re.search(pattern, linked_content, re.IGNORECASE):
            replacement = f'<a href="/articles/?state={state.slug}" class="internal-link text-info">{state.name}</a>'
            linked_content = re.sub(pattern, replacement, linked_content, count=1, flags=re.IGNORECASE)
    
    # Add personality/place links (limited to avoid over-linking)
    for article in articles[:10]:  # Limit to top 10 to avoid performance issues
        if len(article.title.split()) <= 3:  # Only link short titles to avoid false matches
            pattern = r'\b' + re.escape(article.title) + r'\b'
            if re.search(pattern, linked_content, re.IGNORECASE):
                replacement = f'<a href="{article.get_absolute_url()}" class="internal-link text-primary">{article.title}</a>'
                linked_content = re.sub(pattern, replacement, linked_content, count=1, flags=re.IGNORECASE)
    
    return mark_safe(linked_content)


# Helper functions for contextual linking

def _get_category_relationship(current_category, related_category):
    """Determine the relationship between two categories"""
    if related_category == current_category.parent:
        return "parent topic"
    elif related_category.parent == current_category:
        return "subtopic"
    elif related_category.parent == current_category.parent:
        return "related topic"
    else:
        return "related"


@register.simple_tag
def get_article_reading_level(article):
    """Calculate approximate reading level/complexity of an article"""
    if not article.content:
        return "Basic"
    
    import re
    text = re.sub(r'<[^>]+>', '', article.content)
    
    # Simple metrics
    sentences = len(re.split(r'[.!?]+', text))
    words = len(text.split())
    
    if sentences == 0:
        return "Basic"
    
    avg_words_per_sentence = words / sentences
    
    if avg_words_per_sentence < 15:
        return "Basic"
    elif avg_words_per_sentence < 20:
        return "Intermediate"
    else:
        return "Advanced"