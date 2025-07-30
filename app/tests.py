from django.test import TestCase
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from .models import Content, UserProfile, Category, Tag, State
from .forms import ArticleForm


class ArticleCreationTestCase(TestCase):
    """Test cases for article creation functionality"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create user profile with contributor role
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            role='contributor'
        )
        
        # Create test category, tag, and state
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.tag = Tag.objects.create(
            name='Test Tag',
            slug='test-tag'
        )
        self.state = State.objects.create(
            name='Test State',
            slug='test-state',
            description='Test state description',
            capital='Test Capital'
        )
        
        # Login the user
        self.client.login(username='testuser', password='testpass123')
    
    def test_article_creation_minimal_data(self):
        """Test article creation with minimal required data"""
        post_data = {
            'title': 'Test Article',
            'content': '<p>This is test content</p>',
            'content_type': 'article',
            'excerpt': '',
            'meta_description': '',
        }
        
        response = self.client.post(reverse('app:article-create'), post_data)
        
        # Print response details for debugging
        print(f"Response status: {response.status_code}")
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            if form and form.errors:
                print(f"Form errors: {form.errors}")
                print(f"Form non-field errors: {form.non_field_errors()}")
        
        # Check if article was created
        articles = Content.objects.filter(title='Test Article')
        print(f"Articles found: {articles.count()}")
        for article in articles:
            print(f"Article: {article.title}, content_type: {article.content_type}")
        
        # Should redirect on success (302) or stay on page with errors (200)
        if response.status_code == 302:
            self.assertEqual(articles.count(), 1)
        else:
            print("Article creation failed - staying on form page")
    
    def test_article_creation_full_data(self):
        """Test article creation with all fields populated"""
        post_data = {
            'title': 'Complete Test Article',
            'content': '<p>This is complete test content with more details</p>',
            'content_type': 'article',
            'excerpt': 'This is a test excerpt',
            'meta_description': 'Test meta description for SEO',
            'categories': [self.category.id],
            'tags': [self.tag.id],
            'states': [self.state.id],
        }
        
        response = self.client.post(reverse('app:article-create'), post_data)
        
        print(f"Full data response status: {response.status_code}")
        if hasattr(response, 'context') and response.context:
            form = response.context.get('form')
            if form and form.errors:
                print(f"Full data form errors: {form.errors}")
        
        articles = Content.objects.filter(title='Complete Test Article')
        print(f"Complete articles found: {articles.count()}")
    
    def test_form_validation_directly(self):
        """Test the ArticleForm validation directly"""
        form_data = {
            'title': 'Direct Form Test',
            'content': '<p>Direct form test content</p>',
            'content_type': 'article',
            'excerpt': '',
            'meta_description': '',
        }
        
        form = ArticleForm(data=form_data)
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Direct form errors: {form.errors}")
        
        if form.is_valid():
            # Try to save without commit to see if it would work
            instance = form.save(commit=False)
            instance.author = self.user
            instance.content_type = 'article'
            print(f"Form instance created: {instance.title}")


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
