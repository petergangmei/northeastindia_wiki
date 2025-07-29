#!/usr/bin/env python
"""
Simple script to test Schema.org structured data implementation
Run this after activating the virtual environment:
source venv/bin/activate && python test_schema.py
"""

import os
import sys
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.dev')
django.setup()

from app.models import Article
from app.templatetags.schema_tags import (
    detect_content_type, 
    is_person_article, 
    is_place_article, 
    is_event_article,
    generate_content_keywords,
    get_cultural_context,
    extract_geographical_info
)

def test_schema_tags():
    """Test the custom template tags for Schema.org generation"""
    print("=== Testing Schema.org Template Tags ===\n")
    
    # Get a few sample articles
    articles = Article.objects.filter(published=True)[:3]
    
    if not articles:
        print("No published articles found. Please create some test articles first.")
        return
    
    for article in articles:
        print(f"--- Testing Article: {article.title} ---")
        
        # Test content type detection
        content_type = detect_content_type(article)
        print(f"Detected Content Type: {content_type}")
        
        # Test specific type checks
        print(f"Is Person Article: {is_person_article(article)}")
        print(f"Is Place Article: {is_place_article(article)}")
        print(f"Is Event Article: {is_event_article(article)}")
        
        # Test keyword generation
        keywords = generate_content_keywords(article)
        print(f"Generated Keywords ({len(keywords)}): {keywords[:10]}...")  # Show first 10
        
        # Test cultural context
        cultural_context = get_cultural_context(article)
        print(f"Cultural Context: {cultural_context}")
        
        # Test geographical info
        geo_info = extract_geographical_info(article)
        print(f"Geographic Info: {geo_info['region']}, States: {len(geo_info['states'])}")
        
        print("-" * 50)

def test_json_structure():
    """Test if the generated JSON structures are valid"""
    print("\n=== Testing JSON Structure Generation ===\n")
    
    from django.test import RequestFactory
    from django.template.loader import render_to_string
    import json
    import re
    
    factory = RequestFactory()
    article = Article.objects.filter(published=True).first()
    
    if not article:
        print("No published articles found for JSON testing.")
        return
    
    # Create a mock request
    request = factory.get(f'/article/{article.slug}/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['wsgi.url_scheme'] = 'http'
    
    try:
        # Render the template
        html_content = render_to_string('articles/article_detail.html', {
            'article': article,
            'request': request,
            'user': None,
            'related_articles': [],
            'has_edit_permission': False,
            'has_review_permission': False,
            'has_pending_edit': False,
        })
        
        # Extract JSON-LD scripts
        pattern = r'<script type="application/ld\+json">(.*?)</script>'
        matches = re.findall(pattern, html_content, re.DOTALL)
        
        print(f"Found {len(matches)} JSON-LD scripts")
        
        for i, script in enumerate(matches):
            try:
                parsed = json.loads(script.strip())
                print(f"✓ Script #{i+1} - Valid JSON")
                
                # Check for required Schema.org properties
                if '@context' in parsed and '@type' in parsed:
                    print(f"  Schema Type: {parsed['@type']}")
                    if 'name' in parsed:
                        print(f"  Name: {parsed['name']}")
                else:
                    print(f"  ⚠ Missing required Schema.org properties")
                    
            except json.JSONDecodeError as e:
                print(f"✗ Script #{i+1} - Invalid JSON: {e}")
        
    except Exception as e:
        print(f"Template rendering error: {e}")

def show_usage_example():
    """Show example of the generated structured data"""
    print("\n=== Usage Example ===\n")
    print("The enhanced Schema.org implementation includes:")
    print("1. Organization schema for Northeast India Wiki")
    print("2. BreadcrumbList schema for navigation")
    print("3. Dynamic content type detection (Person/Place/Event/Cultural)")
    print("4. FAQ schema for common questions")
    print("5. Geographic information for Northeast India region")
    print("6. Cultural context and mentions extraction")
    print("\nTo validate your structured data:")
    print("1. Use Google's Rich Results Test: https://search.google.com/test/rich-results")
    print("2. Use Schema.org validator: https://validator.schema.org/")
    print("3. Run: python manage.py validate_schema --settings=core.settings.dev")

if __name__ == "__main__":
    test_schema_tags()
    test_json_structure() 
    show_usage_example()