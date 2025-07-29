import json
from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.template.loader import render_to_string
from django.conf import settings
from app.models import Article

class Command(BaseCommand):
    help = 'Validate Schema.org structured data for articles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--article-slug',
            type=str,
            help='Validate specific article by slug',
        )
        parser.add_argument(
            '--validate-online',
            action='store_true',
            help='Use Google Rich Results Test API for validation',
        )

    def handle(self, *args, **options):
        if options['article_slug']:
            articles = Article.objects.filter(slug=options['article_slug'], published=True)
        else:
            articles = Article.objects.filter(published=True)[:5]  # Test first 5 articles

        factory = RequestFactory()
        
        for article in articles:
            self.stdout.write(f"\n=== Validating Schema for: {article.title} ===")
            
            # Create a mock request
            request = factory.get(f'/article/{article.slug}/')
            request.META['HTTP_HOST'] = 'localhost:8000'
            request.META['wsgi.url_scheme'] = 'http'
            
            # Render the template to extract JSON-LD
            try:
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
                json_ld_scripts = self.extract_json_ld(html_content)
                
                for i, script in enumerate(json_ld_scripts):
                    self.stdout.write(f"\n--- JSON-LD Script #{i+1} ---")
                    
                    # Validate JSON syntax
                    try:
                        parsed_json = json.loads(script)
                        self.stdout.write(self.style.SUCCESS("✓ Valid JSON syntax"))
                        
                        # Basic Schema.org validation
                        self.validate_schema_properties(parsed_json)
                        
                        if options['validate_online']:
                            self.validate_with_google_api(script)
                            
                    except json.JSONDecodeError as e:
                        self.stdout.write(self.style.ERROR(f"✗ Invalid JSON: {e}"))
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Template rendering error: {e}"))

    def extract_json_ld(self, html_content):
        """Extract JSON-LD scripts from HTML content"""
        import re
        
        pattern = r'<script type="application/ld\+json">(.*?)</script>'
        matches = re.findall(pattern, html_content, re.DOTALL)
        
        return [match.strip() for match in matches]

    def validate_schema_properties(self, schema_data):
        """Validate basic Schema.org properties"""
        required_props = ['@context', '@type']
        
        for prop in required_props:
            if prop not in schema_data:
                self.stdout.write(self.style.ERROR(f"✗ Missing required property: {prop}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"✓ Found required property: {prop}"))
        
        # Check for Northeast India specific content
        content_str = json.dumps(schema_data).lower()
        ne_indicators = ['northeast india', 'seven sisters', 'assam', 'meghalaya', 'manipur']
        
        found_ne_content = any(indicator in content_str for indicator in ne_indicators)
        if found_ne_content:
            self.stdout.write(self.style.SUCCESS("✓ Contains Northeast India specific content"))
        else:
            self.stdout.write(self.style.WARNING("⚠ Limited Northeast India specific content"))

    def validate_with_google_api(self, json_ld_script):
        """Validate using Google Rich Results Test API (if available)"""
        # Note: This requires setting up Google Rich Results Test API
        # For now, we'll just indicate the feature is available
        self.stdout.write(self.style.WARNING("⚠ Google API validation not implemented yet"))
        
        # Example implementation would be:
        # import requests
        # api_url = "https://searchconsole.googleapis.com/v1/urlTestingTools/richResults:run"
        # headers = {'Authorization': f'Bearer {api_key}'}
        # data = {'url': test_url, 'inspectionUrl': test_url}
        # response = requests.post(api_url, headers=headers, json=data)