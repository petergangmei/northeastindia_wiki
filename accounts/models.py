from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfile(models.Model):
    """
    Extended user profile with additional attributes and role-based permissions
    """
    USER_ROLES = (
        ('viewer', 'Viewer'),
        ('contributor', 'Contributor'),
        ('editor', 'Editor'),
        ('admin', 'Administrator'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='viewer')
    
    # Social media handles for enhanced sharing
    twitter_handle = models.CharField(max_length=50, blank=True, help_text="Twitter handle without @")
    linkedin_profile = models.URLField(blank=True, help_text="LinkedIn profile URL")
    facebook_profile = models.URLField(blank=True, help_text="Facebook profile URL")
    
    # Reputation and contribution tracking
    reputation_points = models.IntegerField(default=0)
    contribution_count = models.IntegerField(default=0)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.user.username})
