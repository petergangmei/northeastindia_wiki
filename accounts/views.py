from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse

from .models import UserProfile
from .forms import CustomUserCreationForm
from app.models import Contribution, Content

# Create alias for backward compatibility since views use Article extensively
Article = Content


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
        return redirect('accounts:profile', username=request.user.username)
    
    context = {
        'user_profile': user_profile,
    }
    
    return render(request, 'users/edit_profile.html', context)


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
                    
                    return redirect('accounts:password-reset-done')
            else:
                # Return to same page but don't reveal that email doesn't exist
                messages.error(request, "An email has been sent with instructions to reset your password if an account with that email exists.")
                return redirect('accounts:password-reset')
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
                return redirect('accounts:password-reset-complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'registration/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "The reset link is invalid or has expired!")
        return redirect('accounts:password-reset')


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
    contributions_count = user_articles.count() + len(recent_edits)
    
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
