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
        ('autoconfirmed', 'Autoconfirmed'),
        ('extended_confirmed', 'Extended Confirmed'),
        ('reviewer', 'Reviewer'),
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
    
    def check_and_update_role(self):
        """
        Check and automatically update user role based on Wikipedia criteria
        """
        from django.utils import timezone
        from datetime import timedelta
        
        # Calculate days since user joined
        days_since_joined = (timezone.now() - self.user.date_joined).days
        
        # Don't downgrade admin or manually assigned roles
        if self.role in ['admin', 'editor', 'reviewer']:
            return
        
        # Auto-promote based on Wikipedia criteria
        if (days_since_joined >= 30 and self.approved_edit_count >= 500 and 
            self.role not in ['extended_confirmed', 'editor', 'admin']):
            # Extended-confirmed (30/500) status
            old_role = self.role
            self.role = 'extended_confirmed'
            self._create_role_change_notification(old_role, 'extended_confirmed')
            
        elif (days_since_joined >= 4 and self.approved_edit_count >= 10 and 
              self.role not in ['autoconfirmed', 'extended_confirmed', 'editor', 'admin']):
            # Autoconfirmed status
            old_role = self.role
            self.role = 'autoconfirmed'
            self._create_role_change_notification(old_role, 'autoconfirmed')
        
        self.save()
    
    def _create_role_change_notification(self, old_role, new_role):
        """Create notification for role change"""
        from app.models import Notification
        
        role_names = dict(self.USER_ROLES)
        message = f"Congratulations! You have been automatically promoted from {role_names.get(old_role, old_role)} to {role_names.get(new_role, new_role)} based on your contributions."
        
        Notification.objects.create(
            user=self.user,
            notification_type='system',
            message=message
        )
    
    def can_review_content(self):
        """Check if user can review content (pending changes, new pages)"""
        return self.role in ['reviewer', 'editor', 'admin']
    
    def can_edit_semi_protected(self):
        """Check if user can edit semi-protected pages"""
        return self.role in ['autoconfirmed', 'extended_confirmed', 'reviewer', 'editor', 'admin']
    
    def can_edit_extended_confirmed_protected(self):
        """Check if user can edit extended-confirmed protected pages"""
        return self.role in ['extended_confirmed', 'reviewer', 'editor', 'admin']
    
    def can_move_pages(self):
        """Check if user can move/rename pages"""
        return self.role in ['autoconfirmed', 'extended_confirmed', 'reviewer', 'editor', 'admin']
    
    def get_role_progress(self):
        """Get progress towards next role"""
        from django.utils import timezone
        from datetime import timedelta
        
        days_since_joined = (timezone.now() - self.user.date_joined).days
        
        if self.role in ['admin', 'editor']:
            return {'next_role': None, 'progress': 100}
        
        # Progress towards extended-confirmed
        if self.role not in ['extended_confirmed']:
            days_needed = max(0, 30 - days_since_joined)
            edits_needed = max(0, 500 - self.approved_edit_count)
            
            if days_needed == 0 and edits_needed == 0:
                return {'next_role': 'extended_confirmed', 'progress': 100, 'ready': True}
            else:
                progress = ((min(30, days_since_joined) / 30) * 50) + ((min(500, self.approved_edit_count) / 500) * 50)
                return {
                    'next_role': 'extended_confirmed',
                    'progress': int(progress),
                    'days_needed': days_needed,
                    'edits_needed': edits_needed
                }
        
        # Progress towards autoconfirmed
        if self.role == 'viewer' or self.role == 'contributor':
            days_needed = max(0, 4 - days_since_joined)
            edits_needed = max(0, 10 - self.approved_edit_count)
            
            if days_needed == 0 and edits_needed == 0:
                return {'next_role': 'autoconfirmed', 'progress': 100, 'ready': True}
            else:
                progress = ((min(4, days_since_joined) / 4) * 50) + ((min(10, self.approved_edit_count) / 10) * 50)
                return {
                    'next_role': 'autoconfirmed',
                    'progress': int(progress),
                    'days_needed': days_needed,
                    'edits_needed': edits_needed
                }
        
        return {'next_role': None, 'progress': 100}
