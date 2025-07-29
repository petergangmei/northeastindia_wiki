"""
Management command to validate and test XML sitemaps

This command helps validate that all sitemap URLs are accessible and
contain valid XML with proper structure for search engine consumption.
"""

from django.core.management.base import BaseCommand
from django.test import Client, override_settings
from django.urls import reverse
from app.sitemaps import SITEMAPS
import xml.etree.ElementTree as ET


class Command(BaseCommand):
    help = 'Validate XML sitemaps for the Northeast India Wiki'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sitemap',
            type=str,
            help='Validate a specific sitemap (e.g., articles, categories)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output for each URL',
        )

    @override_settings(ALLOWED_HOSTS=['testserver', '127.0.0.1', 'localhost'])
    def handle(self, *args, **options):
        client = Client()
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('Validating Northeast India Wiki Sitemaps...\n')
        )

        # Test sitemap index
        self.stdout.write('Testing sitemap index...')
        try:
            response = client.get('/sitemap.xml')
            if response.status_code == 200:
                # Validate XML structure
                ET.fromstring(response.content)
                self.stdout.write(
                    self.style.SUCCESS('✓ Sitemap index accessible and valid XML')
                )
                if verbose:
                    self.stdout.write(f'  Status: {response.status_code}')
                    self.stdout.write(f'  Content-Type: {response.get("Content-Type")}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ Sitemap index failed: {response.status_code}')
                )
        except ET.ParseError as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Sitemap index XML parsing error: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Sitemap index error: {e}')
            )

        # Test individual sitemaps
        sitemaps_to_test = [options['sitemap']] if options['sitemap'] else SITEMAPS.keys()
        
        for sitemap_name in sitemaps_to_test:
            if sitemap_name not in SITEMAPS:
                self.stdout.write(
                    self.style.WARNING(f'Sitemap "{sitemap_name}" not found')
                )
                continue
                
            self.stdout.write(f'\nTesting {sitemap_name} sitemap...')
            
            try:
                url = f'/sitemap-{sitemap_name}.xml'
                response = client.get(url)
                
                if response.status_code == 200:
                    # Validate XML structure
                    root = ET.fromstring(response.content)
                    
                    # Count URLs in sitemap
                    url_count = len(root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'))
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {sitemap_name} sitemap valid ({url_count} URLs)')
                    )
                    
                    if verbose:
                        self.stdout.write(f'  Status: {response.status_code}')
                        self.stdout.write(f'  Content-Type: {response.get("Content-Type")}')
                        self.stdout.write(f'  URLs found: {url_count}')
                        
                        # Show first few URLs as examples
                        urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                        for i, url_elem in enumerate(urls[:3]):
                            self.stdout.write(f'    Example URL {i+1}: {url_elem.text}')
                        if len(urls) > 3:
                            self.stdout.write(f'    ... and {len(urls) - 3} more URLs')
                    
                else:
                    self.stdout.write(
                        self.style.ERROR(f'✗ {sitemap_name} sitemap failed: {response.status_code}')
                    )
                    
            except ET.ParseError as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ {sitemap_name} sitemap XML parsing error: {e}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ {sitemap_name} sitemap error: {e}')
                )

        # Summary
        self.stdout.write(f'\n{"-" * 50}')
        self.stdout.write('Sitemap validation complete!')
        self.stdout.write(
            '\nNext steps:'
            '\n1. Submit sitemap to Google Search Console'
            '\n2. Submit sitemap to Bing Webmaster Tools'
            '\n3. Monitor crawling and indexing in search console'
            '\n4. Test robots.txt at /robots.txt'
        )
        
        # Test robots.txt for good measure
        self.stdout.write('\nTesting robots.txt...')
        try:
            response = client.get('/robots.txt')
            if response.status_code == 200:
                if b'Sitemap:' in response.content:
                    self.stdout.write(
                        self.style.SUCCESS('✓ robots.txt accessible and includes sitemap reference')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠ robots.txt accessible but missing sitemap reference')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'✗ robots.txt failed: {response.status_code}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ robots.txt error: {e}')
            )