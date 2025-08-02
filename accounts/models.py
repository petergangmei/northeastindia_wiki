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
    
    # Wikipedia-style trust and collaboration metrics
    approved_edit_count = models.PositiveIntegerField(default=0, help_text="Number of approved edits")
    rejected_edit_count = models.PositiveIntegerField(default=0, help_text="Number of rejected edits")
    revert_count = models.PositiveIntegerField(default=0, help_text="Number of times user's edits were reverted")
    trust_score = models.FloatField(default=0.0, help_text="Calculated trust score based on edit history")
    auto_approve_edits = models.BooleanField(default=False, help_text="Whether user's edits are auto-approved")
    
    # Collaboration features
    watch_notifications = models.BooleanField(default=True, help_text="Receive notifications for watched articles")
    mention_notifications = models.BooleanField(default=True, help_text="Receive notifications when mentioned")
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.user.username})
    
    def calculate_trust_score(self):
        """
        Calculate Wikipedia-style trust score based on edit history
        Score ranges from 0.0 to 10.0
        """
        total_edits = self.approved_edit_count + self.rejected_edit_count
        
        if total_edits == 0:
            return 0.0
        
        # Base score from approval rate
        approval_rate = self.approved_edit_count / total_edits
        base_score = approval_rate * 5.0  # 0-5 points from approval rate
        
        # Bonus points for volume (diminishing returns)
        volume_bonus = min(2.0, self.approved_edit_count / 50.0)  # Up to 2 points for volume
        
        # Penalty for reverts
        revert_penalty = min(2.0, self.revert_count * 0.1)  # -0.1 per revert, max -2 points
        
        # Time-based bonus (users who've been contributing for longer get slight bonus)
        # This would need to be calculated based on first contribution date
        
        final_score = max(0.0, min(10.0, base_score + volume_bonus - revert_penalty))
        return round(final_score, 2)
    
    def update_trust_score(self):
        """Update and save the trust score"""
        self.trust_score = self.calculate_trust_score()
        
        # Auto-approve edits for highly trusted users
        if self.trust_score >= 7.0 and self.approved_edit_count >= 20:
            self.auto_approve_edits = True
        elif self.trust_score < 5.0 or self.revert_count > 5:
            self.auto_approve_edits = False
        
        self.save()
