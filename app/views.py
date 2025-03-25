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
from django.http import HttpResponse
from difflib import ndiff
import bleach
import string
import random
from .models import UserProfile, Contribution, Article, ArticleRevision, Category, Tag, State, PendingEdit
from .forms import ArticleForm, CustomUserCreationForm

def home(request):
    """
    Home page view
    """
    return render(request, 'home.html')

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
    articles = Article.objects.filter(published=True, review_status='approved')
    
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
    articles = Article.objects.filter(published=True, review_status='approved')
    
    if query:
        # Search in title, content and excerpt
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
        # Search in title, content and excerpt
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

def article_detail(request, slug):
    """
    Display a single article
    """
    article = get_object_or_404(Article, slug=slug)
    
    # Check if article is published or if the user is the author or has appropriate permissions
    is_visible_to_user = article.published
    has_edit_permission = False
    has_review_permission = False
    
    if request.user.is_authenticated:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        is_author = article.author == request.user
        is_editor_or_admin = user_profile.role in ['editor', 'admin'] or request.user.is_staff
        
        # Article is visible to authenticated users who are the author or editors/admins
        is_visible_to_user = is_visible_to_user or is_author or is_editor_or_admin
        
        # Edit permission is for authors, editors, or admins
        has_edit_permission = is_author or is_editor_or_admin
        
        # Review permission is for editors or admins only
        has_review_permission = is_editor_or_admin
    
    if not is_visible_to_user:
        raise Http404("Article not found or not published.")
    
    # Get the top 3 related articles (simple implementation: sharing categories)
    related_articles = []
    if article.categories.exists():
        related_articles = Article.objects.filter(
            categories__in=article.categories.all(),
            published=True
        ).exclude(id=article.id).distinct().order_by('-published_at')[:3]
    
    # Check if there's a pending edit for this article
    has_pending_edit = False
    try:
        pending_edit = article.pending_edit
        has_pending_edit = True
    except:
        pending_edit = None
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'has_edit_permission': has_edit_permission,
        'has_review_permission': has_review_permission,
        'has_pending_edit': has_pending_edit,
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
            ArticleRevision.objects.create(
                article=article,
                user=request.user,
                content=article.content,
                comment="Initial version"
            )
            
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
    pending_edit = None
    try:
        pending_edit = article.pending_edit
    except:
        pass
    
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
                
                # Create or update the pending edit
                if pending_edit:
                    # Update existing pending edit
                    pending_edit.title = title
                    pending_edit.content = cleaned_content
                    pending_edit.excerpt = excerpt
                    pending_edit.meta_description = meta_description
                    pending_edit.references = references
                    pending_edit.categories_ids = categories_ids
                    pending_edit.tags_ids = tags_ids
                    pending_edit.states_ids = states_ids
                    pending_edit.editor = request.user
                    pending_edit.revision_comment = revision_comment
                    
                    # Handle featured image
                    if 'featured_image' in request.FILES:
                        pending_edit.featured_image = request.FILES['featured_image']
                        
                    pending_edit.save()
                else:
                    # Create new pending edit
                    pending_edit = PendingEdit.objects.create(
                        article=article,
                        title=title,
                        content=cleaned_content,
                        excerpt=excerpt,
                        meta_description=meta_description,
                        references=references,
                        editor=request.user,
                        revision_comment=revision_comment,
                        categories_ids=categories_ids,
                        tags_ids=tags_ids,
                        states_ids=states_ids
                    )
                    
                    # Handle featured image
                    if 'featured_image' in request.FILES:
                        pending_edit.featured_image = request.FILES['featured_image']
                        pending_edit.save()
                
                # Check if the user is submitting for review
                submit_for_review = request.POST.get('submit_for_review') == 'true'
                if submit_for_review:
                    # Apply the pending edit and set the article to pending review
                    pending_edit.apply_edit()
                    messages.success(request, 'Article edit submitted for review!')
                else:
                    messages.success(request, 'Draft changes saved! Submit for review when ready.')
                
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
                    ArticleRevision.objects.create(
                        article=updated_article,
                        user=request.user,
                        content=updated_article.content,
                        comment=revision_comment
                    )
                    
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
    revisions = ArticleRevision.objects.filter(article=article).order_by('-created_at')
    
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
    revisions = ArticleRevision.objects.filter(article=article).order_by('-created_at')
    
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
    revision = get_object_or_404(ArticleRevision, id=revision_id, article=article)
    
    context = {
        'article': article,
        'revision': revision,
    }
    
    return render(request, 'articles/article_revision.html', context)

def article_compare(request, slug):
    """
    Compare two different revisions of an article
    """
    article = get_object_or_404(Article, slug=slug)
    
    # Get the revision IDs from request parameters
    from_revision_id = request.GET.get('from_revision')
    to_revision_id = request.GET.get('to_revision')
    
    # Get all revisions for the article for the dropdown
    all_revisions = article.revisions.all()
    
    # If no revisions are specified in the URL, default to the two most recent
    if not all_revisions.exists() or all_revisions.count() < 2:
        messages.warning(request, "At least two revisions are needed to compare.")
        return redirect('app:article-history', slug=slug)
    
    if not from_revision_id or not to_revision_id:
        # Default to comparing the two most recent revisions
        to_revision = all_revisions.order_by('-created_at')[0]
        from_revision = all_revisions.order_by('-created_at')[1]
    else:
        # Get the specified revisions
        from_revision = get_object_or_404(ArticleRevision, id=from_revision_id, article=article)
        to_revision = get_object_or_404(ArticleRevision, id=to_revision_id, article=article)
    
    # Simple diff implementation - more sophisticated diffing can be added
    from difflib import ndiff
    
    # Split content by lines for diffing
    from_lines = from_revision.content.splitlines()
    to_lines = to_revision.content.splitlines()
    
    # Generate diff
    diff = list(ndiff(from_lines, to_lines))
    
    # Format the diff for display
    content_diff_lines = []
    line_num_old = 1
    line_num_new = 1
    
    for line in diff:
        if line.startswith('  '):  # unchanged
            content_diff_lines.append({
                'type': 'unchanged',
                'content': line[2:],
                'line_num_old': line_num_old,
                'line_num_new': line_num_new,
            })
            line_num_old += 1
            line_num_new += 1
        elif line.startswith('- '):  # removed
            content_diff_lines.append({
                'type': 'removed',
                'content': line[2:],
                'line_num_old': line_num_old,
                'line_num_new': None,
            })
            line_num_old += 1
        elif line.startswith('+ '):  # added
            content_diff_lines.append({
                'type': 'added',
                'content': line[2:],
                'line_num_old': None,
                'line_num_new': line_num_new,
            })
            line_num_new += 1
    
    # Get categories and tags for each revision if available
    from_categories = []
    to_categories = []
    from_tags = []
    to_tags = []
    
    context = {
        'article': article,
        'from_revision': from_revision,
        'to_revision': to_revision,
        'all_revisions': all_revisions,
        'content_diff_lines': content_diff_lines,
        'from_categories': from_categories,
        'to_categories': to_categories,
        'from_tags': from_tags,
        'to_tags': to_tags,
    }
    
    return render(request, 'articles/article_compare.html', context)

def category_list(request):
    """
    Display all categories
    """
    # Get all parent categories (main categories)
    main_categories = Category.objects.filter(parent__isnull=True)
    
    # Add article count to each category
    for category in main_categories:
        category.article_count = Article.objects.filter(categories=category, published=True).count()
        category.subcategories = Category.objects.filter(parent=category)
        
        # Get the most recent article in this category
        latest_article = Article.objects.filter(categories=category, published=True).order_by('-published_at').first()
        category.latest_article = latest_article
    
    # Get popular categories based on article count
    popular_categories = []
    for category in Category.objects.all():
        category.article_count = Article.objects.filter(categories=category, published=True).count()
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
            category.article_count = Article.objects.filter(categories=category, published=True).count()
        
        if categories.exists():
            categories_by_letter.append({
                'letter': letter,
                'categories': categories
            })
    
    # Find a featured category (most articles or manually set)
    featured_category = None
    if popular_categories:
        featured_category = popular_categories[0]
        featured_category.article_count = Article.objects.filter(categories=featured_category, published=True).count()
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
    articles = Article.objects.filter(categories=category, published=True)
    
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
    
    # Get related categories (siblings)
    if category.parent:
        related_categories = Category.objects.filter(parent=category.parent).exclude(id=category.id)[:5]
    else:
        # If no parent, show some random categories
        related_categories = Category.objects.exclude(id=category.id).order_by('?')[:5]
    
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
        tag.count = Article.objects.filter(tags=tag, published=True).count()
        
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
    articles = Article.objects.filter(tags=tag, published=True)
    
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
    user_articles = Article.objects.filter(author=user).order_by('-created_at')
    
    # Get only draft articles
    drafts = user_articles.filter(review_status='draft').order_by('-updated_at')
    
    # Get recent article revisions by the user
    recent_edits = ArticleRevision.objects.filter(user=user).order_by('-created_at')
    
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
    pending_articles = Article.objects.filter(review_status='pending')
    
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
    pending_count = Article.objects.filter(review_status='pending').count()
    approved_count = Article.objects.filter(review_status='approved', published=True).count()
    rejected_count = Article.objects.filter(review_status='rejected').count()
    draft_count = Article.objects.filter(review_status='draft').count()
    
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
    revisions = ArticleRevision.objects.filter(article=article).order_by('-created_at')
    
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
            
            messages.success(request, f'Article "{article.title}" has been approved and published.')
            
        elif action == 'reject':
            if not feedback:
                messages.error(request, "Feedback is required when rejecting an article.")
                return redirect('app:article-review', slug=slug)
            
            # Check if this is an edit of an already approved article
            was_previously_approved = False
            previous_revisions = ArticleRevision.objects.filter(article=article).order_by('-created_at')
            if previous_revisions.count() > 1:
                # Check if this article was previously approved
                was_previously_approved = Article.objects.filter(id=article.id, review_status='approved').exists()
            
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
                
                messages.success(request, f'Article "{article.title}" has been rejected.')
        
        else:
            messages.error(request, "Invalid action specified.")
            return redirect('app:article-review', slug=slug)
        
        return redirect('app:article-review-queue')
    
    # If not POST, redirect to review page
    return redirect('app:article-review', slug=slug)
