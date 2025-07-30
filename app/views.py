from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, Http404
from difflib import ndiff
import bleach
import string
import random
from .models import UserProfile, Contribution, Content, Category, Tag, State, Notification

# Create alias for backward compatibility since views use Article extensively
Article = Content
from .forms import ArticleForm, CustomUserCreationForm

# Notification utility functions
def create_notification(user, notification_type, message, content_type='', object_id=None):
    """
    Creates a notification for a user.
    
    Args:
        user: The user to notify
        notification_type: Type of notification (from Notification.NOTIFICATION_TYPES)
        message: The notification message
        content_type: Optional content type (e.g., 'article')
        object_id: Optional ID of the related object
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message,
        content_type=content_type,
        object_id=object_id
    )
    return notification

def home(request):
    """
    Home page view
    """
    # Get Article of the Day
    # For simplicity, we'll get a random approved and published article
    # In a real implementation, you might have a specific selection process
    article_of_the_day = Article.objects.filter(
        content_type='article',
        published=True, 
        review_status='approved'
    ).order_by('?').first()
    
    # Get latest articles (for "Trending" section)
    latest_articles = Article.objects.filter(
        content_type='article',
        published=True, 
        review_status='approved'
    ).order_by('-published_at')[:4]
    
    # Get categories with article counts
    categories = Category.objects.all()
    
    # Prepare categories with article counts
    categories_with_counts = []
    for category in categories[:6]:  # Limit to 6 categories
        article_count = Article.objects.filter(
            content_type='article',
            categories=category,
            published=True,
            review_status='approved'
        ).count()
        
        categories_with_counts.append({
            'category': category,
            'count': article_count
        })
    
    context = {
        'article_of_the_day': article_of_the_day,
        'latest_articles': latest_articles,
        'categories_with_counts': categories_with_counts
    }
    
    return render(request, 'home.html', context)

def user_login(request):
    """
    Custom login view
    """
    if request.user.is_authenticated:
        return redirect('app:home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Check if user has a profile, create one if not
                UserProfile.objects.get_or_create(user=user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('app:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    """
    Custom logout view
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('app:home')

def register(request):
    """
    User registration view
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('app:home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request, username):
    """
    User profile view
    """
    user = get_object_or_404(User, username=username)
    # Get or create user profile to avoid 404 errors
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    contributions = Contribution.objects.filter(user=user).order_by('-created_at')[:10]
    
    context = {
        'user_profile': user_profile,
        'contributions': contributions,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """
    Edit user profile view
    """
    # Get or create user profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle form submission
        user_profile.bio = request.POST.get('bio', '')
        user_profile.location = request.POST.get('location', '')
        user_profile.website = request.POST.get('website', '')
        
        if 'avatar' in request.FILES:
            user_profile.avatar = request.FILES['avatar']
        
        user_profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('app:profile', username=request.user.username)
    
    context = {
        'user_profile': user_profile,
    }
    
    return render(request, 'users/edit_profile.html', context)

# Article Views
def article_list(request):
    """
    List all published articles with filtering options
    """
    articles = Article.objects.filter(content_type='article', published=True, review_status='approved')
    
    # Filtering by category, tag, state, or search query
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    state_slug = request.GET.get('state')
    query = request.GET.get('q')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(categories=category)
    
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        articles = articles.filter(tags=tag)
    
    if state_slug:
        state = get_object_or_404(State, slug=state_slug)
        articles = articles.filter(states=state)
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(articles, 12)  # 12 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for sidebar
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'category_slug': category_slug,
        'tag_slug': tag_slug,
        'state_slug': state_slug,
        'query': query,
    }
    
    return render(request, 'articles/article_list.html', context)

def article_search(request):
    """
    Handle article search with enhanced UI
    """
    query = request.GET.get('q', '')
    articles = Article.objects.filter(content_type='article', published=True, review_status='approved')
    
    if query:
        # Search in title, content and excerpt across all content types
        articles = articles.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(articles, 12)  # 12 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories and states for sidebar
    categories = Category.objects.all()
    states = State.objects.all()
    tags = Tag.objects.all()[:12]  # Get top 12 tags
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'states': states,
        'tags': tags,
        'query': query,
    }
    
    return render(request, 'articles/article_search.html', context)

def article_search_htmx(request):
    """
    HTMX endpoint for live article search on the home page
    """
    query = request.GET.get('q', '')
    articles = None
    
    if query:
        # Search in title, content and excerpt across all content types
        articles = Article.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query),
            published=True, 
            review_status='approved'
        )[:10]  # Limit to top 10 results for performance
    
    context = {
        'articles': articles,
        'query': query,
    }
    
    return render(request, 'articles/search_results_partial.html', context)

def article_detail(request, slug, state_slug=None):
    """
    Display a single article
    Handles both old and new SEO-optimized URL structures
    """
    article = get_object_or_404(Article, slug=slug)
    
    # If state_slug is provided, verify the article belongs to that state
    if state_slug:
        state = get_object_or_404(State, slug=state_slug)
        if not article.states.filter(slug=state_slug).exists():
            # Article doesn't belong to this state, redirect to correct URL
            return redirect(article.get_absolute_url(), permanent=True)
    
    # Check if article is published or if the user is the author or has appropriate permissions
    is_visible_to_user = article.published
    has_edit_permission = False
    has_review_permission = False
    user_profile = None
    
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile
        except UserProfile.DoesNotExist:
            user_profile = None
        
        is_author = article.author == request.user
        is_editor_or_admin = (user_profile and user_profile.role in ['editor', 'admin']) or request.user.is_staff
        
        # Article is visible to authenticated users who are the author or editors/admins
        is_visible_to_user = is_visible_to_user or is_author or is_editor_or_admin
        
        # Edit permission is for authors, editors, or admins
        has_edit_permission = is_author or is_editor_or_admin
        
        # Review permission is for editors or admins only
        has_review_permission = is_editor_or_admin
    
    if not is_visible_to_user:
        raise Http404("Article not found or not published.")
    
    # Get sophisticated related articles using multiple strategies
    from .utils import get_enhanced_related_articles, get_contextual_links_data
    related_articles = get_enhanced_related_articles(article, limit=6)
    
    # Get contextual linking data for widgets
    contextual_data = get_contextual_links_data(article)
    
    # Check if there's a pending edit for this article
    has_pending_edit = False
    try:
        pending_edit = article.pending_edit
        has_pending_edit = True
    except:
        pending_edit = None
    
    # Generate info box data for states
    info_box_data = None
    coordinates = None
    if article.states.exists():
        state = article.states.first()
        # Calculate area in square miles (1 km² = 0.386102 sq mi)
        area_sq_miles = int(state.area * 0.386102) if state.area else None
        # Calculate population density
        pop_density = int(state.population / state.area) if state.population and state.area else None
        
        info_box_data = {
            'status': 'State of India',
            'capital': state.capital,
            'largest_city': 'Chümoukedima–Dimapur' if state.name == 'Nagaland' else None,
            'districts': '17 districts' if state.name == 'Nagaland' else f"{getattr(state, 'districts_count', 'N/A')} districts",
            'government': {
                'Governor': 'La. Ganesan' if state.name == 'Nagaland' else 'TBD',
                'Chief Minister': 'Neiphiu Rio' if state.name == 'Nagaland' else 'TBD'
            },
            'state_legislature': '60 (Assembly seats)',
            'parliament_seats': {
                'Lok Sabha': '1',
                'Rajya Sabha': '1'
            },
            'high_court': 'Gauhati High Court',
            'area': {
                'total': f"{state.area:,} km² ({area_sq_miles:,} sq mi)" if state.area and area_sq_miles else None,
                'rank': '25th among Indian states' if state.name == 'Nagaland' else None
            },
            'elevation': {
                'Highest': 'Mount Saramati 3,826 m (12,552 ft)' if state.name == 'Nagaland' else 'N/A',
                'Lowest': 'Dhansiri Valley 194 m (636 ft)' if state.name == 'Nagaland' else 'N/A'
            },
            'population': {
                'total': f"{state.population:,}" if state.population else None,
                'rank': '25th among Indian states' if state.name == 'Nagaland' else None,
                'density': f"{pop_density}/km²" if pop_density else None,
                'urban': '28.6%' if state.name == 'Nagaland' else None,
                'rural': '71.4%' if state.name == 'Nagaland' else None
            },
            'demonym': 'Naga' if state.name == 'Nagaland' else f"{state.name}se",
            'languages': {
                'Official': state.languages if state.languages else 'English',
                'Additional official': None
            },
            'time_zone': 'IST (UTC+05:30)',
            'iso_code': f"IN-{state.name[:2].upper()}",
            'vehicle_registration': f"{state.name[:2].upper()}",
            'hdi': {
                'value': '0.679 (medium)' if state.name == 'Nagaland' else 'N/A',
                'year': '2021',
                'rank': '20th among Indian states' if state.name == 'Nagaland' else None
            },
            'literacy': '80.11%' if state.name == 'Nagaland' else None,
            'sex_ratio': '931 ♀/1000 ♂' if state.name == 'Nagaland' else None,
            'website': f"https://{state.name.lower()}.gov.in"
        }
        
        # Add coordinates if available (example coordinates for Nagaland)
        if state.name == 'Nagaland':
            coordinates = {
                'lat': 25.6751,
                'lng': 94.1086,
                'display': '25.67°N 94.10°E'
            }
        # Add more state coordinates as needed
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'has_edit_permission': has_edit_permission,
        'has_review_permission': has_review_permission,
        'has_pending_edit': has_pending_edit,
        'contextual_data': contextual_data,
        'info_box_data': info_box_data,
        'coordinates': coordinates,
        'user_profile': user_profile,
    }
    
    return render(request, 'articles/article_detail.html', context)

@login_required
def article_create(request):
    """
    Create a new article
    """
    # Check if user has permission (contributor or higher)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.role == 'viewer':
        messages.error(request, "You don't have permission to create articles. Please request contributor status.")
        return redirect('app:home')
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            # Create but don't save the article instance yet
            article = form.save(commit=False)
            article.author = request.user
            article.review_status = 'draft'
            
            # Clean HTML content with bleach to prevent XSS attacks
            allowed_tags = [
                'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 
                'u', 'a', 'img', 'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 
                'table', 'thead', 'tbody', 'tr', 'th', 'td', 'br', 'hr'
            ]
            allowed_attrs = {
                'a': ['href', 'title', 'target'],
                'img': ['src', 'alt', 'title', 'width', 'height'],
            }
            article.content = bleach.clean(
                article.content, 
                tags=allowed_tags, 
                attributes=allowed_attrs,
                strip=True
            )
            
            # Check if the user is submitting for review
            submit_for_review = request.POST.get('submit_for_review') == 'true'
            if submit_for_review:
                article.review_status = 'pending'
            
            # Save the article
            article.save()
            
            # Save the many-to-many fields
            form.save_m2m()
            
            # Create initial revision
            # TODO: Implement revision tracking with new Content model
            # ArticleRevision.objects.create(
            #     article=article,
            #     user=request.user,
            #     content=article.content,
            #     comment="Initial version"
            # )
            
            # Record the contribution
            Contribution.objects.create(
                user=request.user,
                contribution_type='article_create',
                content_type='article',
                object_id=article.id,
                points_earned=10,  # Adjust point value as needed
                approved=True
            )
            
            # Update user's contribution count
            user_profile.contribution_count += 1
            user_profile.reputation_points += 10  # Adjust point value as needed
            user_profile.save()
            
            messages.success(request, 'Article created successfully! It will be published after review.')
            return redirect('app:article-detail', slug=article.slug)
    else:
        form = ArticleForm()
    
    context = {
        'form': form,
        'title': 'Create New Article',
    }
    
    return render(request, 'articles/article_form.html', context)

@login_required
def article_edit(request, slug):
    """
    Edit an existing article
    """
    # Get the article
    article = get_object_or_404(Article, slug=slug)
    
    # Check if user has permission to edit (author, editor, or admin)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.user != article.author and user_profile.role not in ['editor', 'admin'] and not request.user.is_staff:
        messages.error(request, "You don't have permission to edit this article.")
        return redirect('app:article-detail', slug=article.slug)
    
    # Check if there's already a pending edit for this article
    # TODO: Implement pending edits with new Content model
    pending_edit = None
    # try:
    #     pending_edit = article.pending_edit
    # except:
    #     pass
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            # Keep track of original content for revision
            original_content = article.content
            
            # Different handling based on article status
            if article.review_status == 'approved':
                # For approved articles, create/update a pending edit instead of modifying the article directly
                
                # Get the revision comment
                revision_comment = form.cleaned_data.get('revision_comment', 'Updated article')
                if not revision_comment:
                    revision_comment = 'Updated article'
                
                # Get values from the form
                title = form.cleaned_data.get('title')
                content = form.cleaned_data.get('content')
                excerpt = form.cleaned_data.get('excerpt', '')
                meta_description = form.cleaned_data.get('meta_description', '')
                references = form.cleaned_data.get('references', '')
                
                # Clean HTML content
                allowed_tags = [
                    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 
                    'u', 'a', 'img', 'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 
                    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'br', 'hr'
                ]
                allowed_attrs = {
                    'a': ['href', 'title', 'target'],
                    'img': ['src', 'alt', 'title', 'width', 'height'],
                }
                cleaned_content = bleach.clean(
                    content, 
                    tags=allowed_tags, 
                    attributes=allowed_attrs,
                    strip=True
                )
                
                # Get M2M fields as IDs
                categories_ids = [cat.id for cat in form.cleaned_data.get('categories', [])]
                tags_ids = [tag.id for tag in form.cleaned_data.get('tags', [])]
                states_ids = [state.id for state in form.cleaned_data.get('states', [])]
                
                # TODO: Implement pending edits with new Content model
                # For now, directly update the article
                updated_article = form.save(commit=False)
                updated_article.last_edited_by = request.user
                
                # Clean HTML content
                allowed_tags = [
                    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 
                    'u', 'a', 'img', 'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 
                    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'br', 'hr'
                ]
                allowed_attrs = {
                    'a': ['href', 'title', 'target'],
                    'img': ['src', 'alt', 'title', 'width', 'height'],
                }
                updated_article.content = bleach.clean(
                    updated_article.content, 
                    tags=allowed_tags, 
                    attributes=allowed_attrs,
                    strip=True
                )
                
                # Check if the user is submitting for review
                submit_for_review = request.POST.get('submit_for_review') == 'true'
                if submit_for_review:
                    updated_article.review_status = 'pending'
                
                updated_article.save()
                form.save_m2m()
                
                messages.success(request, 'Article updated successfully!')
                
                # Record the contribution
                Contribution.objects.create(
                    user=request.user,
                    contribution_type='article_edit',
                    content_type='article',
                    object_id=article.id,
                    points_earned=5,  # Adjust point value as needed
                    approved=True
                )
                
                # Update user's contribution count
                user_profile.contribution_count += 1
                user_profile.reputation_points += 5  # Adjust point value as needed
                user_profile.save()
                
            else:
                # For non-approved articles, update them directly
                
                # Create but don't save the article instance yet
                updated_article = form.save(commit=False)
                
                # Set last edited by
                updated_article.last_edited_by = request.user
                
                # Clean HTML content
                allowed_tags = [
                    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'em', 
                    'u', 'a', 'img', 'blockquote', 'code', 'pre', 'ul', 'ol', 'li', 
                    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'br', 'hr'
                ]
                allowed_attrs = {
                    'a': ['href', 'title', 'target'],
                    'img': ['src', 'alt', 'title', 'width', 'height'],
                }
                updated_article.content = bleach.clean(
                    updated_article.content, 
                    tags=allowed_tags, 
                    attributes=allowed_attrs,
                    strip=True
                )
                
                # Check if the user is submitting for review
                submit_for_review = request.POST.get('submit_for_review') == 'true'
                if submit_for_review and updated_article.review_status in ['draft', 'rejected']:
                    updated_article.review_status = 'pending'
                
                # Save the article
                updated_article.save()
                
                # Save the many-to-many fields
                form.save_m2m()
                
                # Get the revision comment
                revision_comment = form.cleaned_data.get('revision_comment', 'Updated article')
                if not revision_comment:
                    revision_comment = 'Updated article'
                
                # Create revision if content changed
                if original_content != updated_article.content:
                    # TODO: Implement revision tracking with new Content model
                    # ArticleRevision.objects.create(
                    #     article=updated_article,
                    #     user=request.user,
                    #     content=updated_article.content,
                    #     comment=revision_comment
                    # )
                    pass
                    
                    # Record the contribution
                    Contribution.objects.create(
                        user=request.user,
                        contribution_type='article_edit',
                        content_type='article',
                        object_id=updated_article.id,
                        points_earned=5,  # Adjust point value as needed
                        approved=True
                    )
                    
                    # Update user's contribution count
                    user_profile.contribution_count += 1
                    user_profile.reputation_points += 5  # Adjust point value as needed
                    user_profile.save()
                
                messages.success(request, 'Article updated successfully!')
            
            return redirect('app:article-detail', slug=article.slug)
    else:
        # For GET requests, show the form with either the article data or pending edit data
        if pending_edit and article.review_status == 'approved':
            # If there's a pending edit, load it instead of the article
            initial_data = {
                'title': pending_edit.title or article.title,
                'content': pending_edit.content,
                'excerpt': pending_edit.excerpt,
                'meta_description': pending_edit.meta_description,
                'references': pending_edit.references,
                'revision_comment': pending_edit.revision_comment,
            }
            
            # Initialize the form with initial data
            form = ArticleForm(instance=article, initial=initial_data)
            
            # We'll handle the m2m fields and featured image in the template
        else:
            # Just load the article as normal
            form = ArticleForm(instance=article)
    
    # Get revision history
    # TODO: Implement revision tracking with new Content model
    revisions = []  # ArticleRevision.objects.filter(article=article).order_by('-created_at')
    
    context = {
        'form': form,
        'article': article,
        'revisions': revisions,
        'pending_edit': pending_edit,
        'title': 'Edit Article',
    }
    
    return render(request, 'articles/article_form.html', context)

def article_history(request, slug):
    """
    View the revision history of an article
    """
    article = get_object_or_404(Article, slug=slug)
    # TODO: Implement revision tracking with new Content model
    revisions = []  # ArticleRevision.objects.filter(article=article).order_by('-created_at')
    
    context = {
        'article': article,
        'revisions': revisions,
    }
    
    return render(request, 'articles/article_history.html', context)

def article_revision(request, slug, revision_id):
    """
    View a specific revision of an article
    """
    article = get_object_or_404(Article, slug=slug)
    # TODO: Implement revision tracking with new Content model
    # revision = get_object_or_404(ArticleRevision, id=revision_id, article=article)
    revision = None
    
    context = {
        'article': article,
        'revision': revision,
    }
    
    return render(request, 'articles/article_revision.html', context)

def article_compare(request, slug):
    """
    Compare two different revisions of an article
    TODO: Implement revision comparison with new Content model
    """
    article = get_object_or_404(Article, slug=slug)
    
    # TODO: Implement revision tracking and comparison with new Content model
    messages.info(request, "Revision comparison is not yet implemented with the new content model.")
    return redirect('app:article-detail', slug=slug)

def category_list(request):
    """
    Display all categories
    """
    # Get all parent categories (main categories)
    main_categories = Category.objects.filter(parent__isnull=True)
    
    # Add article count to each category
    for category in main_categories:
        category.article_count = Article.objects.filter(content_type='article', categories=category, published=True).count()
        category.subcategories = Category.objects.filter(parent=category)
        
        # Get the most recent article in this category
        latest_article = Article.objects.filter(content_type='article', categories=category, published=True).order_by('-published_at').first()
        category.latest_article = latest_article
    
    # Get popular categories based on article count
    popular_categories = []
    for category in Category.objects.all():
        category.article_count = Article.objects.filter(content_type='article', categories=category, published=True).count()
        if category.article_count > 0:
            popular_categories.append(category)
    
    popular_categories = sorted(popular_categories, key=lambda x: x.article_count, reverse=True)[:8]
    
    # Create alphabetical listing
    categories_by_letter = []
    import string
    
    for letter in string.ascii_uppercase:
        categories = Category.objects.filter(name__istartswith=letter)
        
        # Add article count to each category
        for category in categories:
            category.article_count = Article.objects.filter(content_type='article', categories=category, published=True).count()
        
        if categories.exists():
            categories_by_letter.append({
                'letter': letter,
                'categories': categories
            })
    
    # Find a featured category (most articles or manually set)
    featured_category = None
    if popular_categories:
        featured_category = popular_categories[0]
        featured_category.article_count = Article.objects.filter(content_type='article', categories=featured_category, published=True).count()
        featured_category.subcategories = Category.objects.filter(parent=featured_category)
    
    context = {
        'main_categories': main_categories,
        'popular_categories': popular_categories,
        'categories_by_letter': categories_by_letter,
        'featured_category': featured_category,
    }
    
    return render(request, 'articles/categories.html', context)

def category_articles(request, slug):
    """
    Display articles for a specific category
    """
    category = get_object_or_404(Category, slug=slug)
    
    # Get filter parameters
    sort = request.GET.get('sort', 'newest')
    selected_subcategories = request.GET.getlist('subcategory')
    selected_tags = request.GET.getlist('tag')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Start with all published articles in this category
    articles = Article.objects.filter(content_type='article', categories=category, published=True)
    
    # Filter by subcategories if selected
    if selected_subcategories:
        subcategory_objects = Category.objects.filter(id__in=selected_subcategories)
        articles = articles.filter(categories__in=subcategory_objects).distinct()
        selected_subcategories_names = [cat.name for cat in subcategory_objects]
    else:
        selected_subcategories_names = []
    
    # Filter by tags if selected
    if selected_tags:
        tag_objects = Tag.objects.filter(id__in=selected_tags)
        articles = articles.filter(tags__in=tag_objects).distinct()
        selected_tags_names = [tag.name for tag in tag_objects]
    else:
        selected_tags_names = []
    
    # Filter by date range if provided
    if date_from:
        try:
            articles = articles.filter(published_at__gte=date_from)
        except ValueError:
            messages.warning(request, "Invalid 'from' date format.")
    
    if date_to:
        try:
            articles = articles.filter(published_at__lte=date_to)
        except ValueError:
            messages.warning(request, "Invalid 'to' date format.")
    
    # Apply sorting
    if sort == 'newest':
        articles = articles.order_by('-published_at')
    elif sort == 'oldest':
        articles = articles.order_by('published_at')
    elif sort == 'az':
        articles = articles.order_by('title')
    elif sort == 'za':
        articles = articles.order_by('-title')
    elif sort == 'popular':
        # If view count is tracked, use it for popularity
        # For simplicity, we'll just use a random order here
        articles = articles.order_by('?')
    
    # Check if any filters are applied
    is_filtered = bool(selected_subcategories or selected_tags or date_from or date_to or sort != 'newest')
    
    # Get subcategories for filtering
    subcategories = Category.objects.filter(parent=category)
    
    # Get associated tags for this category's articles
    tags = Tag.objects.filter(article_items__categories=category).distinct()
    
    # Get statistics for sidebar
    total_articles = articles.count()
    contributors = User.objects.filter(article_items__categories=category).distinct()
    contributors_count = contributors.count()
    last_updated = articles.order_by('-updated_at').values_list('updated_at', flat=True).first()
    
    # Get related categories (siblings) and cross-references
    from .utils import get_discover_more_suggestions
    related_categories = []
    if category.parent:
        related_categories = Category.objects.filter(parent=category.parent).exclude(id=category.id)[:5]
    else:
        # If no parent, show some random categories
        related_categories = Category.objects.exclude(id=category.id).order_by('?')[:5]
    
    # Get discovery suggestions for better cross-linking
    category_suggestions = get_discover_more_suggestions('category', category, limit=4)
    
    # Pagination
    paginator = Paginator(articles, 10)  # Show 10 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'articles': page_obj,
        'subcategories': subcategories,
        'tags': tags,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'total_articles': total_articles,
        'contributors_count': contributors_count,
        'last_updated': last_updated,
        'related_categories': related_categories,
        'category_suggestions': category_suggestions,
        'sort': sort,
        'selected_subcategories': selected_subcategories,
        'selected_tags': selected_tags,
        'selected_subcategories_names': selected_subcategories_names,
        'selected_tags_names': selected_tags_names,
        'date_from': date_from,
        'date_to': date_to,
        'is_filtered': is_filtered,
    }
    
    return render(request, 'articles/category_articles.html', context)

def tag_list(request):
    """
    Display all tags
    """
    tags = Tag.objects.all()
    
    # Add article count and styling info to each tag
    for tag in tags:
        tag.count = Article.objects.filter(content_type='article', tags=tag, published=True).count()
        
        # Assign a size class based on count for the tag cloud
        if tag.count == 0:
            tag.size = 1
        elif tag.count < 5:
            tag.size = 2
        elif tag.count < 10:
            tag.size = 3
        elif tag.count < 20:
            tag.size = 4
        else:
            tag.size = 5
            
        # Assign a random color for variety in the tag cloud
        colors = ['primary', 'secondary', 'success', 'info', 'warning']
        import random
        tag.color = random.choice(colors)
    
    # Create alphabetical listing
    alphabet = []
    tags_by_letter = []
    import string
    
    for letter in string.ascii_uppercase:
        tag_group = tags.filter(name__istartswith=letter)
        if tag_group.exists():
            alphabet.append({'letter': letter, 'has_tags': True})
            tags_by_letter.append({'letter': letter, 'tags': tag_group})
        else:
            alphabet.append({'letter': letter, 'has_tags': False})
    
    # Popular tags
    popular_tags = sorted(tags, key=lambda x: x.count, reverse=True)[:9]
    
    context = {
        'tags': tags,
        'alphabet': alphabet,
        'tags_by_letter': tags_by_letter,
        'popular_tags': popular_tags,
    }
    
    return render(request, 'articles/article_tags.html', context)

def tag_articles(request, slug):
    """
    Display articles for a specific tag
    """
    tag = get_object_or_404(Tag, slug=slug)
    
    # Get filter parameters
    sort = request.GET.get('sort', 'newest')
    selected_categories = request.GET.getlist('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Start with all published articles with this tag
    articles = Article.objects.filter(content_type='article', tags=tag, published=True)
    
    # Filter by categories if selected
    if selected_categories:
        category_objects = Category.objects.filter(id__in=selected_categories)
        articles = articles.filter(categories__in=category_objects).distinct()
        selected_categories_names = [cat.name for cat in category_objects]
    else:
        selected_categories_names = []
    
    # Filter by date range if provided
    if date_from:
        try:
            articles = articles.filter(published_at__gte=date_from)
        except ValueError:
            messages.warning(request, "Invalid 'from' date format.")
    
    if date_to:
        try:
            articles = articles.filter(published_at__lte=date_to)
        except ValueError:
            messages.warning(request, "Invalid 'to' date format.")
    
    # Apply sorting
    if sort == 'newest':
        articles = articles.order_by('-published_at')
    elif sort == 'oldest':
        articles = articles.order_by('published_at')
    elif sort == 'az':
        articles = articles.order_by('title')
    elif sort == 'za':
        articles = articles.order_by('-title')
    elif sort == 'popular':
        # If view count is tracked, use it for popularity
        # For simplicity, we'll just use a random order here
        articles = articles.order_by('?')
    
    # Check if any filters are applied
    is_filtered = bool(selected_categories or date_from or date_to or sort != 'newest')
    
    # Get categories for filtering
    categories = Category.objects.filter(article_items__tags=tag).distinct()
    
    # Get statistics for sidebar
    total_articles = articles.count()
    contributors = User.objects.filter(article_items__tags=tag).distinct()
    contributors_count = contributors.count()
    last_updated = articles.order_by('-updated_at').values_list('updated_at', flat=True).first()
    
    # Get related tags based on co-occurrence in articles
    article_ids = articles.values_list('id', flat=True)
    related_tags = Tag.objects.filter(article_items__id__in=article_ids).exclude(id=tag.id).distinct()[:10]
    
    # Get discovery suggestions for better cross-linking
    tag_suggestions = get_discover_more_suggestions('tag', tag, limit=5)
    
    # Pagination
    paginator = Paginator(articles, 10)  # Show 10 articles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'articles': page_obj,
        'categories': categories,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj,
        'total_articles': total_articles,
        'contributors_count': contributors_count,
        'last_updated': last_updated,
        'related_tags': related_tags,
        'tag_suggestions': tag_suggestions,
        'sort': sort,
        'selected_categories': selected_categories,
        'selected_categories_names': selected_categories_names,
        'date_from': date_from,
        'date_to': date_to,
        'is_filtered': is_filtered,
    }
    
    return render(request, 'articles/tag_articles.html', context)

def password_reset_request(request):
    """
    Custom password reset view
    """
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                for user in associated_users:
                    # Generate token and UID
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    
                    # Build email
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password_reset_email.html"
                    context = {
                        "email": user.email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'Northeast India Wiki',
                        "uid": uid,
                        "user": user,
                        'token': token,
                        'protocol': 'http' if request.is_secure() else 'https',
                    }
                    email_content = render_to_string(email_template_name, context)
                    
                    try:
                        send_mail(subject, email_content, 'noreply@northeastindia.wiki', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    
                    return redirect('app:password-reset-done')
            else:
                # Return to same page but don't reveal that email doesn't exist
                messages.error(request, "An email has been sent with instructions to reset your password if an account with that email exists.")
                return redirect('app:password-reset')
    else:
        form = PasswordResetForm()
    
    return render(request, 'registration/password_reset_form.html', {'form': form})

def password_reset_done(request):
    """
    Custom password reset done view
    """
    return render(request, 'registration/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    """
    Custom password reset confirm view
    """
    try:
        # Validate the user by getting the uid
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    # Check if the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and log in now.")
                return redirect('app:password-reset-complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'registration/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "The reset link is invalid or has expired!")
        return redirect('app:password-reset')

def password_reset_complete(request):
    """
    Custom password reset complete view
    """
    return render(request, 'registration/password_reset_complete.html')

@login_required
def user_contributions(request):
    """
    Display the user's contributions including articles, drafts, and recent edits
    """
    user = request.user
    active_tab = request.GET.get('tab', 'articles')
    
    # Get all articles created by the user
    user_articles = Article.objects.filter(content_type='article', author=user).order_by('-created_at')
    
    # Get only draft articles
    drafts = user_articles.filter(review_status='draft').order_by('-updated_at')
    
    # Get recent article revisions by the user
    # TODO: Implement revision tracking with new Content model
    recent_edits = []  # ArticleRevision.objects.filter(user=user).order_by('-created_at')
    
    # Calculate total contributions
    contributions_count = user_articles.count() + recent_edits.count()
    
    # Pagination for articles tab
    articles_paginator = Paginator(user_articles, 10)
    articles_page_number = request.GET.get('page', 1)
    articles_page_obj = articles_paginator.get_page(articles_page_number)
    
    # Pagination for edits tab
    edits_paginator = Paginator(recent_edits, 10)
    edits_page_number = request.GET.get('page', 1) if active_tab == 'edits' else 1
    edits_page_obj = edits_paginator.get_page(edits_page_number)
    
    # Pagination for drafts tab
    drafts_paginator = Paginator(drafts, 10)
    drafts_page_number = request.GET.get('page', 1) if active_tab == 'drafts' else 1
    drafts_page_obj = drafts_paginator.get_page(drafts_page_number)
    
    context = {
        'user_articles': articles_page_obj,
        'recent_edits': edits_page_obj,
        'drafts': drafts_page_obj,
        'articles_page_obj': articles_page_obj,
        'edits_page_obj': edits_page_obj,
        'drafts_page_obj': drafts_page_obj,
        'contributions_count': contributions_count
    }
    
    return render(request, 'users/contributions.html', context)

@login_required
def article_delete(request, slug):
    """
    Handle article deletion
    """
    article = get_object_or_404(Article, slug=slug)
    
    # Check if user has permission to delete (author, editor, or admin)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.user != article.author and user_profile.role not in ['editor', 'admin'] and not request.user.is_staff:
        messages.error(request, "You don't have permission to delete this article.")
        return redirect('app:article-detail', slug=article.slug)
    
    if request.method == 'POST':
        article_title = article.title
        
        # Delete the article
        article.delete()
        
        # Update user's stats if they were the author
        if request.user == article.author:
            user_profile.contribution_count = max(0, user_profile.contribution_count - 1)
            user_profile.save()
        
        messages.success(request, f'Article "{article_title}" has been deleted.')
        return redirect('app:user-contributions')
    
    # If not POST, redirect to article detail
    return redirect('app:article-detail', slug=slug)

@login_required
def article_review_queue(request):
    """
    Display a queue of articles that need review
    """
    # Check if user has permission (editor or admin)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.role not in ['editor', 'admin'] and not request.user.is_staff:
        messages.error(request, "You don't have permission to access the review queue.")
        return redirect('app:home')
    
    # Get search query
    query = request.GET.get('q')
    
    # Get sort parameter
    sort = request.GET.get('sort', 'newest')
    
    # Get all pending articles
    pending_articles = Article.objects.filter(content_type='article', review_status='pending')
    
    # Apply search if provided
    if query:
        pending_articles = pending_articles.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(excerpt__icontains=query) |
            Q(author__username__icontains=query)
        )
    
    # Apply sorting
    if sort == 'oldest':
        pending_articles = pending_articles.order_by('created_at')
    else:  # Default to newest
        pending_articles = pending_articles.order_by('-created_at')
    
    # Get counts for dashboard stats
    pending_count = Article.objects.filter(content_type='article', review_status='pending').count()
    approved_count = Article.objects.filter(content_type='article', review_status='approved', published=True).count()
    rejected_count = Article.objects.filter(content_type='article', review_status='rejected').count()
    draft_count = Article.objects.filter(content_type='article', review_status='draft').count()
    
    # Pagination
    paginator = Paginator(pending_articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pending_articles': page_obj,
        'page_obj': page_obj,
        'sort': sort,
        'query': query,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'draft_count': draft_count,
    }
    
    return render(request, 'articles/review_queue.html', context)

@login_required
def article_review(request, slug):
    """
    Review a specific article
    """
    # Check if user has permission (editor or admin)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.role not in ['editor', 'admin'] and not request.user.is_staff:
        messages.error(request, "You don't have permission to review articles.")
        return redirect('app:article-detail', slug=slug)
    
    # Get the article
    article = get_object_or_404(Article, slug=slug)
    
    # Get revision history
    # TODO: Implement revision tracking with new Content model
    revisions = []  # ArticleRevision.objects.filter(article=article).order_by('-created_at')
    
    context = {
        'article': article,
        'revisions': revisions,
    }
    
    return render(request, 'articles/article_review.html', context)

@login_required
def article_review_action(request, slug):
    """
    Handle article review actions (approve or reject)
    """
    # Check if user has permission (editor or admin)
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if user_profile.role not in ['editor', 'admin'] and not request.user.is_staff:
        messages.error(request, "You don't have permission to review articles.")
        return redirect('app:article-detail', slug=slug)
    
    # Get the article
    article = get_object_or_404(Article, slug=slug)
    
    # Check if the article is pending review
    if article.review_status != 'pending':
        messages.warning(request, "This article is not pending review.")
        return redirect('app:article-review-queue')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        feedback = request.POST.get('feedback', '')
        
        if action == 'approve':
            # Update article status
            article.review_status = 'approved'
            article.published = True
            if not article.published_at:
                article.published_at = timezone.now()
            article.save()
            
            # Create a contribution record for the author
            if feedback:
                contribution_note = f"Article approved with feedback: {feedback}"
            else:
                contribution_note = "Article approved"
                
            Contribution.objects.create(
                user=article.author,
                contribution_type='article_published',
                content_type='article',
                object_id=article.id,
                notes=contribution_note,
                points_earned=20,  # Adjust point value as needed
                approved=True,
                approved_by=request.user
            )
            
            # Update author's reputation points
            author_profile = UserProfile.objects.get(user=article.author)
            author_profile.reputation_points += 20  # Adjust point value as needed
            author_profile.save()
            
            # Create notification for author
            notification_message = f"Your article '{article.title}' has been approved and published."
            if feedback:
                notification_message += f" Reviewer feedback: {feedback}"
            create_notification(
                user=article.author,
                notification_type='approval',
                message=notification_message,
                content_type='article',
                object_id=article.id
            )
            
            messages.success(request, f'Article "{article.title}" has been approved and published.')
            
        elif action == 'reject':
            if not feedback:
                messages.error(request, "Feedback is required when rejecting an article.")
                return redirect('app:article-review', slug=slug)
            
            # Check if this is an edit of an already approved article
            was_previously_approved = False
            # TODO: Implement revision tracking with new Content model
            # previous_revisions = ArticleRevision.objects.filter(article=article).order_by('-created_at')
            # For now, assume it's a new article
            # if previous_revisions.count() > 1:
            #     # Check if this article was previously approved
            #     was_previously_approved = Article.objects.filter(id=article.id, review_status='approved').exists()
            
            if was_previously_approved:
                # This is an edit to an already approved article that's being rejected
                # Revert to the last approved version
                article.review_status = 'approved'
                article.save()
                
                # Create a contribution record with the rejection reason
                Contribution.objects.create(
                    user=article.last_edited_by or article.author,
                    contribution_type='article_rejected',
                    content_type='article',
                    object_id=article.id,
                    notes=f"Article edit rejected. Reason: {feedback}",
                    points_earned=0,
                    approved=False,
                    approved_by=request.user
                )
                
                # Create notification for editor
                user_to_notify = article.last_edited_by or article.author
                notification_message = f"Your edit to article '{article.title}' has been rejected. Reason: {feedback}"
                create_notification(
                    user=user_to_notify,
                    notification_type='rejection',
                    message=notification_message,
                    content_type='article',
                    object_id=article.id
                )
                
                messages.success(request, f'Edit to article "{article.title}" has been rejected. The previous approved version remains published.')
            else:
                # This is a new article that's being rejected
                # Update article status
                article.review_status = 'rejected'
                article.save()
                
                # Create a contribution record with the rejection reason
                Contribution.objects.create(
                    user=article.author,
                    contribution_type='article_rejected',
                    content_type='article',
                    object_id=article.id,
                    notes=f"Article rejected. Reason: {feedback}",
                    points_earned=0,
                    approved=False,
                    approved_by=request.user
                )
                
                # Create notification for author
                notification_message = f"Your article '{article.title}' has been rejected. Reason: {feedback}"
                create_notification(
                    user=article.author,
                    notification_type='rejection',
                    message=notification_message,
                    content_type='article',
                    object_id=article.id
                )
                
                messages.success(request, f'Article "{article.title}" has been rejected.')
        
        else:
            messages.error(request, "Invalid action specified.")
            return redirect('app:article-review', slug=slug)
        
        return redirect('app:article-review-queue')
    
    # If not POST, redirect to review page
    return redirect('app:article-review', slug=slug)

# Notification Views
@login_required
def notification_list(request):
    """
    View all user notifications
    """
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Enhance notifications with additional context for articles
    for notification in notifications:
        if notification.content_type == 'article' and notification.object_id:
            try:
                article = Article.objects.get(id=notification.object_id)
                notification.article_slug = article.slug
            except Article.DoesNotExist:
                notification.article_slug = None
    
    # Pagination
    paginator = Paginator(notifications, 15)  # 15 notifications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'unread_count': notifications.filter(read=False).count(),
    }
    
    return render(request, 'notifications/notification_list.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    
    # Check if the request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponse('OK')
    
    # If not AJAX, redirect back to notifications list
    return redirect('app:notification-list')

@login_required
def mark_all_notifications_read(request):
    """
    Mark all notifications as read
    """
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    
    # Check if the request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponse('OK')
    
    # If not AJAX, redirect back to notifications list
    return redirect('app:notification-list')

@login_required
def delete_notification(request, notification_id):
    """
    Delete a notification
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    
    # Check if the request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponse('OK')
    
    # If not AJAX, redirect back to notifications list
    return redirect('app:notification-list')

@login_required
def delete_all_notifications(request):
    """
    Delete all read notifications
    """
    Notification.objects.filter(user=request.user, read=True).delete()
    
    # Check if the request is AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return HttpResponse('OK')
    
    # If not AJAX, redirect back to notifications list
    return redirect('app:notification-list')


def robots_txt(request):
    """
    Generate robots.txt file for search engine crawlers
    
    This view creates a dynamic robots.txt that optimizes search engine crawling
    for the Northeast India Wiki while protecting private areas:
    
    ALLOWED PATHS (Public Content):
    - / (Home page with article of the day)
    - /articles/ (All published articles about Northeast India)
    - /categories/ (Category-based article organization)
    - /tags/ (Tag-based article classification)
    - /static/ (CSS, JS, images for proper rendering)
    
    BLOCKED PATHS (Private/Admin Areas):
    - /admin/ (Django admin panel)
    - /profile/edit/ (User profile editing)
    - /notifications/ (User notifications)
    - /articles/review-queue/ (Admin moderation)
    - /articles/*/edit/ (Article editing forms)
    - /articles/*/history/ (Version control pages)
    - /contributions/ (User contribution tracking)
    - /media/ (User-uploaded content that might be private)
    - Authentication pages (login, register, password reset)
    
    CRAWL OPTIMIZATION:
    - Different crawl delays for major search engines
    - Blocks aggressive SEO crawlers that don't add value
    - Includes sitemap reference for efficient indexing
    
    This ensures search engines can efficiently discover and index
    Northeast India cultural content while respecting user privacy.
    """
    robots_content = """User-agent: *

# Allow crawling of public content about Northeast India
Allow: /
Allow: /articles/
Allow: /categories/
Allow: /tags/
Allow: /static/css/
Allow: /static/js/
Allow: /static/images/

# Allow SEO-optimized URLs for better indexing
Allow: /personalities/
Allow: /culture/
Allow: /festivals/
Allow: /places/
Allow: /heritage/
Allow: /history/
Allow: /traditional-crafts/
Allow: /food/
Allow: /music/
Allow: /dance/
Allow: /literature/
Allow: /states/
Allow: /northeast-india/

# Block admin and moderation areas
Disallow: /admin/
Disallow: /profile/edit/
Disallow: /notifications/
Disallow: /articles/review-queue/
Disallow: /articles/*/review/
Disallow: /articles/*/edit/
Disallow: /articles/*/delete/
Disallow: /articles/*/history/
Disallow: /articles/*/revision/
Disallow: /articles/*/compare/
Disallow: /contributions/

# Block search result pages to avoid duplicate content
Disallow: /articles/search/?*
Disallow: /articles/search-htmx/

# Block authentication and user management pages
Disallow: /login/
Disallow: /logout/
Disallow: /register/
Disallow: /password-reset*

# Block user-generated media that might contain private content
Disallow: /media/

# Block profile pages except public profile views
Disallow: /profile/edit/

# General crawl delay to prevent server overload
Crawl-delay: 1

# Specific rules for major search engines
User-agent: Googlebot
Crawl-delay: 0.5

User-agent: Bingbot
Crawl-delay: 1

User-agent: Slurp
Crawl-delay: 2

# Block aggressive crawlers
User-agent: SemrushBot
Disallow: /

User-agent: AhrefsBot
Disallow: /

User-agent: MJ12bot
Disallow: /

# Sitemap reference for search engines
Sitemap: {scheme}://{host}/sitemap.xml""".format(
        scheme=request.scheme,
        host=request.get_host()
    )
    
    return HttpResponse(robots_content, content_type='text/plain')


# SEO-Optimized Views for Northeast India Content

def state_list(request):
    """
    Display list of all Northeast Indian states
    """
    states = State.objects.all().order_by('name')
    
    context = {
        'states': states,
        'page_title': 'Northeast Indian States',
        'meta_description': 'Explore the eight states of Northeast India - Assam, Arunachal Pradesh, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, and Tripura.',
    }
    return render(request, 'states/state_list.html', context)


def state_detail(request, state_slug):
    """
    Display detailed information about a specific state
    """
    state = get_object_or_404(State, slug=state_slug)
    
    # Get articles related to this state
    articles = Article.objects.filter(
        content_type='article',
        states=state,
        published=True,
        review_status='approved'
    ).order_by('-published_at')[:10]
    
    # Get article counts by category for this state
    categories = Category.objects.all()
    category_counts = {}
    for category in categories:
        count = Article.objects.filter(
            content_type='article',
            states=state,
            categories=category,
            published=True,
            review_status='approved'
        ).count()
        if count > 0:
            category_counts[category] = count
    
    context = {
        'state': state,
        'articles': articles,
        'category_counts': category_counts,
        'page_title': f'{state.name} - Northeast India',
        'meta_description': f'Discover {state.name}, one of the northeastern states of India. Learn about its culture, history, festivals, and notable personalities.',
    }
    return render(request, 'states/state_detail.html', context)


def northeast_overview(request):
    """
    Regional overview of Northeast India
    """
    states = State.objects.all().order_by('name')
    featured_articles = Article.objects.filter(
        content_type='article',
        published=True,
        review_status='featured'
    ).order_by('-published_at')[:6]
    
    context = {
        'states': states,
        'featured_articles': featured_articles,
        'page_title': 'Northeast India - Seven Sisters & Sikkim',
        'meta_description': 'Comprehensive guide to Northeast India covering the Seven Sisters states and Sikkim. Explore rich culture, diverse traditions, and fascinating history.',
    }
    return render(request, 'regional/northeast_overview.html', context)


def seven_sisters(request):
    """
    Information about the Seven Sisters states
    """
    seven_sisters_states = State.objects.filter(
        slug__in=['assam', 'arunachal-pradesh', 'manipur', 'meghalaya', 'mizoram', 'nagaland', 'tripura']
    ).order_by('name')
    
    context = {
        'states': seven_sisters_states,
        'page_title': 'Seven Sisters States of Northeast India',
        'meta_description': 'Learn about the Seven Sisters - the northeastern states of India known for their rich cultural diversity and natural beauty.',
    }
    return render(request, 'regional/seven_sisters.html', context)


def northeast_culture(request):
    """
    Cultural overview of Northeast India
    """
    cultural_articles = Article.objects.filter(
        content_type='article',
        categories__slug='culture',
        published=True,
        review_status='approved'
    ).order_by('-published_at')[:20]
    
    states = State.objects.all().order_by('name')
    
    context = {
        'articles': cultural_articles,
        'states': states,
        'page_title': 'Culture of Northeast India',
        'meta_description': 'Explore the rich and diverse culture of Northeast India including traditional crafts, music, dance, festivals, and customs.',
    }
    return render(request, 'regional/northeast_culture.html', context)


def northeast_heritage(request):
    """
    Heritage sites and traditions of Northeast India
    """
    heritage_articles = Article.objects.filter(
        content_type='article',
        categories__slug='heritage',
        published=True,
        review_status='approved'
    ).order_by('-published_at')[:20]
    
    context = {
        'articles': heritage_articles,
        'page_title': 'Heritage of Northeast India',
        'meta_description': 'Discover the rich heritage of Northeast India including historical sites, traditional practices, and cultural monuments.',
    }
    return render(request, 'regional/northeast_heritage.html', context)


def category_articles_list(request, category_slug):
    """
    Display articles for a specific category across all states
    """
    category = get_object_or_404(Category, slug=category_slug)
    
    articles = Article.objects.filter(
        content_type='article',
        categories=category,
        published=True,
        review_status='approved'
    ).order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get state counts for this category
    states = State.objects.all()
    state_counts = {}
    for state in states:
        count = Article.objects.filter(
            content_type='article',
            categories=category,
            states=state,
            published=True,
            review_status='approved'
        ).count()
        if count > 0:
            state_counts[state] = count
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'state_counts': state_counts,
        'page_title': f'{category.name} in Northeast India',
        'meta_description': f'Explore {category.name.lower()} from Northeast India. Discover articles about {category.name.lower()} from the eight northeastern states.',
    }
    return render(request, 'categories/category_articles_list.html', context)


def state_category_articles(request, state_slug, category_slug):
    """
    Display articles for a specific category within a specific state
    """
    state = get_object_or_404(State, slug=state_slug)
    category = get_object_or_404(Category, slug=category_slug)
    
    articles = Article.objects.filter(
        content_type='article',
        categories=category,
        states=state,
        published=True,
        review_status='approved'
    ).order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'state': state,
        'category': category,
        'page_obj': page_obj,
        'page_title': f'{category.name} in {state.name}',
        'meta_description': f'Explore {category.name.lower()} from {state.name}. Discover articles about {category.name.lower()} specific to {state.name}, Northeast India.',
    }
    return render(request, 'categories/state_category_articles.html', context)


def article_redirect(request, slug):
    """
    Handle redirects from old URL structure to new SEO-optimized URLs
    Maintains backward compatibility
    """
    article = get_object_or_404(Article, slug=slug)
    
    # Get the SEO-optimized URL
    seo_url = article.get_seo_url()
    
    # If the SEO URL is different from the current URL, redirect
    if seo_url != f"/articles/{slug}/":
        return redirect(seo_url, permanent=True)
    
    # Otherwise, use the original article detail view
    return article_detail(request, slug)


# SEO Landing Page Views
def personalities_landing(request):
    """
    SEO-optimized landing page for personalities category
    """
    # Get all states for the region selector
    states = State.objects.all().order_by('name')
    
    # Get personality category
    personality_category = get_object_or_404(Category, slug='personalities')
    
    # Get featured personalities (latest published)
    featured_personalities = Article.objects.filter(
        content_type='article',
        categories=personality_category,
        published=True
    ).select_related('author').prefetch_related('categories', 'states')[:6]
    
    # Get personalities by state
    personalities_by_state = {}
    for state in states:
        state_personalities = Article.objects.filter(
            content_type='article',
            categories=personality_category,
            states=state,
            published=True
        ).select_related('author')[:3]
        if state_personalities.exists():
            personalities_by_state[state] = state_personalities
    
    context = {
        'page_title': 'Notable Personalities of Northeast India',
        'meta_description': 'Discover the inspiring stories of notable personalities from Northeast India - leaders, artists, writers, and change-makers who shaped the region.',
        'category': personality_category,
        'states': states,
        'featured_articles': featured_personalities,
        'articles_by_state': personalities_by_state,
        'canonical_url': request.build_absolute_uri('/personalities/'),
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Northeast India', 'url': '/northeast-india/'},
            {'name': 'Personalities', 'url': '/personalities/'}
        ]
    }
    
    return render(request, 'categories/personalities_landing.html', context)


def culture_landing(request):
    """
    SEO-optimized landing page for culture category
    """
    states = State.objects.all().order_by('name')
    culture_category = get_object_or_404(Category, slug='culture')
    
    # Get featured cultural articles
    featured_culture = Article.objects.filter(
        content_type='article',
        categories=culture_category,
        published=True
    ).select_related('author').prefetch_related('categories', 'states')[:6]
    
    # Get culture articles by state
    culture_by_state = {}
    for state in states:
        state_culture = Article.objects.filter(
            content_type='article',
            categories=culture_category,
            states=state,
            published=True
        ).select_related('author')[:3]
        if state_culture.exists():
            culture_by_state[state] = state_culture
    
    context = {
        'page_title': 'Cultural Heritage of Northeast India',
        'meta_description': 'Explore the rich cultural heritage of Northeast India - traditions, art forms, music, dance, and customs of the eight sister states.',
        'category': culture_category,
        'states': states,
        'featured_articles': featured_culture,
        'articles_by_state': culture_by_state,
        'canonical_url': request.build_absolute_uri('/culture/'),
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Northeast India', 'url': '/northeast-india/'},
            {'name': 'Culture', 'url': '/culture/'}
        ]
    }
    
    return render(request, 'categories/culture_landing.html', context)


def festivals_landing(request):
    """
    SEO-optimized landing page for festivals category
    """
    states = State.objects.all().order_by('name')
    festivals_category = get_object_or_404(Category, slug='festivals')
    
    # Get featured festivals
    featured_festivals = Article.objects.filter(
        content_type='article',
        categories=festivals_category,
        published=True
    ).select_related('author').prefetch_related('categories', 'states')[:6]
    
    # Get festivals by state
    festivals_by_state = {}
    for state in states:
        state_festivals = Article.objects.filter(
            content_type='article',
            categories=festivals_category,
            states=state,
            published=True
        ).select_related('author')[:3]
        if state_festivals.exists():
            festivals_by_state[state] = state_festivals
    
    context = {
        'page_title': 'Festivals of Northeast India',
        'meta_description': 'Discover the vibrant festivals of Northeast India - traditional celebrations, cultural events, and seasonal festivities across the eight states.',
        'category': festivals_category,
        'states': states,
        'featured_articles': featured_festivals,
        'articles_by_state': festivals_by_state,
        'canonical_url': request.build_absolute_uri('/festivals/'),
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Northeast India', 'url': '/northeast-india/'},
            {'name': 'Festivals', 'url': '/festivals/'}
        ]
    }
    
    return render(request, 'categories/festivals_landing.html', context)


def places_landing(request):
    """
    SEO-optimized landing page for places category
    """
    states = State.objects.all().order_by('name')
    places_category = get_object_or_404(Category, slug='places')
    
    # Get featured places
    featured_places = Article.objects.filter(
        content_type='article',
        categories=places_category,
        published=True
    ).select_related('author').prefetch_related('categories', 'states')[:6]
    
    # Get places by state
    places_by_state = {}
    for state in states:
        state_places = Article.objects.filter(
            content_type='article',
            categories=places_category,
            states=state,
            published=True
        ).select_related('author')[:3]
        if state_places.exists():
            places_by_state[state] = state_places
    
    context = {
        'page_title': 'Places to Visit in Northeast India',
        'meta_description': 'Explore breathtaking destinations in Northeast India - monasteries, national parks, hill stations, and cultural sites across the region.',
        'category': places_category,
        'states': states,
        'featured_articles': featured_places,
        'articles_by_state': places_by_state,
        'canonical_url': request.build_absolute_uri('/places/'),
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Northeast India', 'url': '/northeast-india/'},
            {'name': 'Places', 'url': '/places/'}
        ]
    }
    
    return render(request, 'categories/places_landing.html', context)


def heritage_landing(request):
    """
    SEO-optimized landing page for heritage category
    """
    states = State.objects.all().order_by('name')
    heritage_category = get_object_or_404(Category, slug='heritage')
    
    # Get featured heritage sites
    featured_heritage = Article.objects.filter(
        content_type='article',
        categories=heritage_category,
        published=True
    ).select_related('author').prefetch_related('categories', 'states')[:6]
    
    # Get heritage by state
    heritage_by_state = {}
    for state in states:
        state_heritage = Article.objects.filter(
            content_type='article',
            categories=heritage_category,
            states=state,
            published=True
        ).select_related('author')[:3]
        if state_heritage.exists():
            heritage_by_state[state] = state_heritage
    
    context = {
        'page_title': 'Heritage Sites of Northeast India',
        'meta_description': 'Discover the rich heritage of Northeast India - archaeological sites, historical monuments, traditional architecture, and cultural landmarks.',
        'category': heritage_category,
        'states': states,
        'featured_articles': featured_heritage,
        'articles_by_state': heritage_by_state,
        'canonical_url': request.build_absolute_uri('/heritage/'),
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Northeast India', 'url': '/northeast-india/'},
            {'name': 'Heritage', 'url': '/heritage/'}
        ]
    }
    
    return render(request, 'categories/heritage_landing.html', context)


def seven_sisters(request):
    """
    SEO-optimized page about the Seven Sister States
    """
    # Get the seven sister states (excluding Sikkim)
    sister_states = State.objects.exclude(slug='sikkim').order_by('name')
    
    # Get overview articles for each state
    state_overviews = {}
    for state in sister_states:
        # Get the most comprehensive article about this state
        overview = Article.objects.filter(
            content_type='article',
            states=state,
            published=True
        ).select_related('author').prefetch_related('categories').first()
        if overview:
            state_overviews[state] = overview
    
    context = {
        'page_title': 'Seven Sister States of Northeast India',
        'meta_description': 'Complete guide to the Seven Sister States of Northeast India - Assam, Arunachal Pradesh, Manipur, Meghalaya, Mizoram, Nagaland, and Tripura.',
        'states': sister_states,
        'state_overviews': state_overviews,
        'canonical_url': request.build_absolute_uri('/northeast-india/seven-sisters/'),
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Northeast India', 'url': '/northeast-india/'},
            {'name': 'Seven Sister States', 'url': '/northeast-india/seven-sisters/'}
        ]
    }
    
    return render(request, 'regional/seven_sisters.html', context)


def personalities_list(request):
    """
    Display all personality articles
    """
    try:
        personalities_category = Category.objects.get(slug='personalities')
    except Category.DoesNotExist:
        personalities_category = None
    
    if personalities_category:
        articles = Article.objects.filter(
            content_type='article',
            categories=personalities_category,
            published=True,
            review_status='approved'
        ).select_related('author').prefetch_related('categories', 'states').order_by('-created_at')
    else:
        # Fallback: filter by content type or title patterns
        articles = Article.objects.filter(
            content_type='article',
            published=True,
            review_status='approved'
        ).filter(
            Q(title__icontains='biography') | 
            Q(title__icontains='personality') |
            Q(content__icontains='biography') |
            Q(content__icontains='personality')
        ).select_related('author').prefetch_related('categories', 'states').order_by('-created_at')
    
    context = {
        'articles': articles,
        'category': personalities_category,
        'page_title': 'Personalities of Northeast India',
        'meta_description': 'Discover notable personalities, leaders, and influential figures from Northeast India.',
    }
    
    return render(request, 'articles/article_list.html', context)


def culture_list(request):
    """
    Display all culture articles
    """
    try:
        culture_category = Category.objects.get(slug='culture')
    except Category.DoesNotExist:
        culture_category = None
    
    if culture_category:
        articles = Article.objects.filter(
            content_type='article',
            categories=culture_category,
            published=True,
            review_status='approved'
        ).select_related('author').prefetch_related('categories', 'states').order_by('-created_at')
    else:
        # Fallback: filter by content patterns
        articles = Article.objects.filter(
            content_type='article',
            published=True,
            review_status='approved'
        ).filter(
            Q(title__icontains='culture') | 
            Q(title__icontains='tradition') |
            Q(content__icontains='culture') |
            Q(content__icontains='tradition')
        ).select_related('author').prefetch_related('categories', 'states').order_by('-created_at')
    
    context = {
        'articles': articles,
        'category': culture_category,
        'page_title': 'Culture of Northeast India',
        'meta_description': 'Explore the rich cultural heritage, traditions, and customs of Northeast India.',
    }
    
    return render(request, 'articles/article_list.html', context)


def festivals_list(request):
    """
    Display all festival articles
    """
    try:
        festivals_category = Category.objects.get(slug='festivals')
    except Category.DoesNotExist:
        festivals_category = None
    
    if festivals_category:
        articles = Article.objects.filter(
            categories=festivals_category,
            published=True,
            review_status='approved'
        ).select_related('author').prefetch_related('categories', 'states').order_by('-created_at')
    else:
        # Fallback: filter by content patterns
        articles = Article.objects.filter(
            published=True,
            review_status='approved'
        ).filter(
            Q(title__icontains='festival') | 
            Q(title__icontains='celebration') |
            Q(content__icontains='festival') |
            Q(content__icontains='celebration')
        ).select_related('author').prefetch_related('categories', 'states').order_by('-created_at')
    
    context = {
        'articles': articles,
        'category': festivals_category,
        'page_title': 'Festivals of Northeast India',
        'meta_description': 'Discover the vibrant festivals and celebrations of Northeast India.',
    }
    
    return render(request, 'articles/article_list.html', context)


def places_list(request):
    """
    Display all places articles
    """
    try:
        places_category = Category.objects.get(slug='places')
    except Category.DoesNotExist:
        places_category = None
    
    if places_category:
        articles = Article.objects.filter(
            categories=places_category,
            published=True,
            review_status='approved'
        ).select_related('author').prefetch_related('categories', 'states').order_by('-created_at')
    else:
        # Fallback: filter by content patterns
        articles = Article.objects.filter(
            published=True,
            review_status='approved'
        ).filter(
            Q(title__icontains='place') | 
            Q(title__icontains='destination') |
            Q(title__icontains='tourism') |
            Q(content__icontains='place') |
            Q(content__icontains='destination')
        ).select_related('author').prefetch_related('categories', 'states').order_by('-created_at')
    
    context = {
        'articles': articles,
        'category': places_category,
        'page_title': 'Places in Northeast India',
        'meta_description': 'Explore beautiful places, destinations, and tourist attractions in Northeast India.',
    }
    
    return render(request, 'articles/article_list.html', context)


def tribal_culture_list(request):
    """
    Display tribal culture articles
    """
    # This is more specific - look for tribal culture content
    articles = Article.objects.filter(
        published=True,
        review_status='approved'
    ).filter(
        Q(title__icontains='tribal') | 
        Q(title__icontains='tribe') |
        Q(content__icontains='tribal') |
        Q(content__icontains='tribe')
    ).select_related('author').prefetch_related('categories', 'states').order_by('-created_at')
    
    context = {
        'articles': articles,
        'category': None,
        'page_title': 'Tribal Culture of Northeast India',
        'meta_description': 'Learn about the diverse tribal cultures and communities of Northeast India.',
    }
    
    return render(request, 'articles/article_list.html', context)
