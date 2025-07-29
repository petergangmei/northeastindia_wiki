from django.test import TestCase
from django.urls import reverse
from django.test import Client


class RobotsTxtTestCase(TestCase):
    """Test cases for robots.txt functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_robots_txt_accessible(self):
        """Test that robots.txt is accessible at /robots.txt"""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
    
    def test_robots_txt_content(self):
        """Test that robots.txt contains expected directives"""
        response = self.client.get('/robots.txt')
        content = response.content.decode('utf-8')
        
        # Test basic structure
        self.assertIn('User-agent: *', content)
        self.assertIn('Crawl-delay: 1', content)
        self.assertIn('Sitemap:', content)
        
        # Test allowed paths
        self.assertIn('Allow: /', content)
        self.assertIn('Allow: /articles/', content)
        self.assertIn('Allow: /categories/', content)
        self.assertIn('Allow: /tags/', content)
        self.assertIn('Allow: /static/', content)
        
        # Test disallowed paths
        self.assertIn('Disallow: /admin/', content)
        self.assertIn('Disallow: /profile/edit/', content)
        self.assertIn('Disallow: /notifications/', content)
        self.assertIn('Disallow: /articles/review-queue/', content)
        self.assertIn('Disallow: /media/', content)
    
    def test_robots_txt_url_reverse(self):
        """Test that robots.txt URL can be reversed"""
        url = reverse('app:robots-txt')
        self.assertEqual(url, '/robots.txt')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
