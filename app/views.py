from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Contribution

def home(request):
    """
    Home page view
    """
    return render(request, 'home.html')

def register(request):
    """
    User registration view
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('app:home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request, username):
    """
    User profile view
    """
    user = get_object_or_404(User, username=username)
    user_profile = get_object_or_404(UserProfile, user=user)
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
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
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
