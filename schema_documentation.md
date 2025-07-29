# Schema.org Structured Data Implementation for Northeast India Wiki

## Overview

This implementation adds comprehensive Schema.org structured data markup to help Google and other search engines better understand the Northeast India content. The system automatically detects content types and generates appropriate structured data for articles about personalities, places, cultural events, and other Northeast India topics.

## Features Implemented

### 1. Organization Schema
- **Location**: `templates/base.html`
- **Purpose**: Establishes Northeast India Wiki as an authoritative source
- **Includes**: 
  - Organization details and mission
  - Geographic coverage (Northeast India region)
  - Knowledge areas (Seven Sisters states, culture, heritage)
  - Search functionality

### 2. Dynamic Content Type Detection
- **Location**: `app/templatetags/schema_tags.py`
- **Functions**:
  - `detect_content_type()` - Analyzes article content to determine primary type
  - `is_person_article()` - Detects personality/biography articles
  - `is_place_article()` - Detects location-based content
  - `is_event_article()` - Detects festivals and cultural events
  - `is_cultural_article()` - Detects cultural elements and traditions

### 3. Enhanced Article Schema
- **Location**: `templates/articles/article_detail.html`
- **Features**:
  - Multi-type schema support (Article + Person/Place/Event/Cultural)
  - Automatic keyword generation based on content analysis
  - Reading time calculation
  - Cultural context extraction
  - Geographic information for Northeast India region
  - Mentions of notable personalities and places

### 4. BreadcrumbList Schema
- **Purpose**: Helps search engines understand site navigation
- **Dynamic**: Adapts based on article categories and states
- **Structure**: Home → Articles → Category → Article

### 5. FAQ Schema
- **Purpose**: Enables rich snippets for common questions
- **Questions**:
  - "What is [Article Title]?"
  - "Where is [Article Title] located?"
- **Answers**: Generated from article excerpts and geographic data

## Content Type Detection Logic

### Person Articles
**Keywords**: biography, personality, leader, artist, writer, politician, musician, dancer, activist, freedom fighter, chief minister, governor, poet, author, singer, actor, filmmaker

**Additional Schema Properties**:
- `birthDate` and `deathDate` (extracted from content)
- `birthPlace` (Northeast India region)
- `nationality` (India)
- `knowsAbout` (Northeast India Culture)

### Place Articles  
**Keywords**: city, town, village, district, state, river, mountain, hill, valley, lake, park, sanctuary, temple, monastery, palace, fort, archaeological, tourist, destination, capital

**Additional Schema Properties**:
- `address` with Northeast India region
- `containedInPlace` (Northeast India)
- Geographic coordinates for the region

### Event Articles
**Keywords**: festival, celebration, ceremony, tradition, ritual, dance, music, cultural, harvest, spring, new year, religious, tribal, community, annual, seasonal

**Additional Schema Properties**:
- `eventStatus` (EventScheduled)
- `location` (Northeast India)
- `organizer` (Traditional Communities)

### Cultural Articles
**Keywords**: art, craft, cuisine, food, dish, recipe, attire, dress, costume, language, dialect, literature, folklore, legend, tradition, custom, belief, practice, heritage

**Additional Schema Properties**:
- `culturalContext` (Northeast Indian Culture)
- `artform` (Traditional Northeast Indian Art)
- `genre` (Cultural Heritage)

## Geographic Information

### Northeast India Region
- **Coordinates**: Latitude 26.2006, Longitude 92.9376 (central point)
- **Bounding Box**: "21.57 87.01 29.50 97.40"
- **States Covered**: Assam, Arunachal Pradesh, Manipur, Meghalaya, Mizoram, Nagaland, Tripura, Sikkim

### State-Specific Data
- Each article linked to specific states includes:
  - State name and capital
  - Address region (state within Northeast India)
  - Cultural and historical context

## SEO Benefits

### Rich Snippets
- Article information with reading time
- Author and publication dates
- Geographic context
- Cultural significance

### Knowledge Graph
- Organization establishment in Google's knowledge base
- Regional authority for Northeast India content
- Cultural and historical expertise recognition

### Local SEO
- Geographic relevance for Northeast India searches
- State-specific content optimization
- Cultural tourism and heritage queries

## Implementation Files

### Template Tags
- `app/templatetags/schema_tags.py` - Core logic for content analysis and schema generation

### Templates
- `templates/base.html` - Organization and website schema
- `templates/articles/article_detail.html` - Article-specific structured data

### Management Commands
- `app/management/commands/validate_schema.py` - Schema validation tool

### Testing
- `test_schema.py` - Test script for template tags and JSON generation

## Usage Examples

### Testing the Implementation
```bash
# Activate virtual environment
source venv/bin/activate

# Test template tags
python test_schema.py

# Validate schema for specific article
python manage.py validate_schema --article-slug="your-article-slug" --settings=core.settings.dev

# Validate multiple articles
python manage.py validate_schema --settings=core.settings.dev
```

### Validation Tools
1. **Google Rich Results Test**: https://search.google.com/test/rich-results
2. **Schema.org Validator**: https://validator.schema.org/
3. **Structured Data Testing Tool**: https://developers.google.com/search/docs/appearance/structured-data

## Content Detection Keywords

### Person Detection
- Primary: biography, personality, leader, artist, writer
- Secondary: politician, musician, dancer, activist, poet, author

### Place Detection  
- Primary: city, town, village, district, state
- Secondary: river, mountain, hill, valley, lake, tourist destination

### Event Detection
- Primary: festival, celebration, ceremony, tradition
- Secondary: ritual, dance, music, cultural, harvest, religious

### Cultural Detection
- Primary: art, craft, cuisine, food, tradition
- Secondary: attire, language, literature, folklore, heritage

## Best Practices

### Content Creation
1. Use descriptive titles that include location context
2. Add proper categories and tags for better detection
3. Include geographic information in article content
4. Mention relevant states in the Northeast India region

### SEO Optimization
1. Ensure articles have proper meta descriptions
2. Use featured images with appropriate alt text
3. Include references and sources for credibility
4. Link articles to relevant states and categories

### Schema Validation
1. Regularly test structured data with Google's tools
2. Monitor search console for structured data errors
3. Update schema as content types evolve
4. Validate JSON-LD syntax before deployment

## Regional Context Enhancement

### Seven Sisters States
The implementation specifically recognizes and optimizes for:
- **Assam**: Cultural hub, largest state
- **Arunachal Pradesh**: Eastern frontier, tribal diversity
- **Manipur**: Martial arts, classical dance
- **Meghalaya**: Khasi, Jaintia, Garo tribes
- **Mizoram**: Christian majority, unique culture
- **Nagaland**: Hornbill festival, tribal heritage
- **Tripura**: Royal heritage, Bengali influence
- **Sikkim**: Buddhist culture, Himalayan state

### Cultural Elements
- Traditional festivals and celebrations
- Indigenous art forms and crafts
- Regional cuisines and food traditions
- Historical personalities and leaders
- Sacred sites and natural landmarks
- Languages and literary traditions

This comprehensive implementation ensures that Northeast India content is properly understood and indexed by search engines, improving discoverability and providing rich, contextual information to users searching for content about this culturally rich region of India.