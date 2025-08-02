from django.db.models.signals import post_save
from django.dispatch import receiver
from app.models import ContentRevision


@receiver(post_save, sender=ContentRevision)
def update_user_role_on_edit_approval(sender, instance, created, **kwargs):
    """
    Automatically check and update user roles when a revision is approved
    """
    if instance.status == 'approved' and instance.editor:
        try:
            profile = instance.editor.profile
            # Update approved edit count
            profile.approved_edit_count += 1
            profile.save()
            
            # Check for role promotion
            profile.check_and_update_role()
        except:
            # If user doesn't have a profile, skip
            pass