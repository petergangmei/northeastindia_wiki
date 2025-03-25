from app.models import Notification

def notifications(request):
    """
    Context processor to make notifications available in all templates
    
    Returns:
        dict: Context with user's unread notification count and recent notifications
    """
    if request.user.is_authenticated:
        # Get unread notification count
        unread_count = Notification.objects.filter(user=request.user, read=False).count()
        
        # Get recent notifications (limit to 5)
        recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        
        return {
            'unread_notification_count': unread_count,
            'recent_notifications': recent_notifications,
        }
    
    return {
        'unread_notification_count': 0,
        'recent_notifications': [],
    } 