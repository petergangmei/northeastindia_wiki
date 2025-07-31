from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile) 
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'location', 'reputation_points', 'contribution_count']
    list_filter = ['role', 'email_notifications']
    search_fields = ['user__username', 'user__email', 'location']
    readonly_fields = ['reputation_points', 'contribution_count']
