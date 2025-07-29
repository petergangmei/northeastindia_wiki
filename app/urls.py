from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'app'  # Define namespace for URL names

urlpatterns = [
    path('', views.home, name='home'),
    
    # SEO and crawlers
    path('robots.txt', views.robots_txt, name='robots-txt'),
    
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # Password management
    path('password-reset/', views.password_reset_request, name='password-reset'),
    path('password-reset/done/', views.password_reset_done, name='password-reset-done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password-reset-confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password-reset-complete'),
    
    # User profile URLs - edit_profile must come before profile/<str:username>/
    path('profile/edit/', views.edit_profile, name='profile-edit'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('contributions/', views.user_contributions, name='user-contributions'),
    
    # Notification URLs
    path('notifications/', views.notification_list, name='notification-list'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete-notification'),
    path('notifications/delete-all-read/', views.delete_all_notifications, name='delete-all-notifications'),
    
    # Article URLs
    path('articles/', views.article_list, name='article-list'),
    path('articles/search/', views.article_search, name='article-search'),
    path('articles/search-htmx/', views.article_search_htmx, name='article-search-htmx'),
    path('articles/create/', views.article_create, name='article-create'),
    
    # Article Review - Place review URLs before article detail to avoid URL conflicts
    path('articles/review-queue/', views.article_review_queue, name='article-review-queue'),
    path('articles/<slug:slug>/review/', views.article_review, name='article-review'),
    path('articles/<slug:slug>/review/action/', views.article_review_action, name='article-review-action'),
    
    # Article detail and related URLs
    path('articles/<slug:slug>/', views.article_detail, name='article-detail'),
    path('articles/<slug:slug>/edit/', views.article_edit, name='article-edit'),
    path('articles/<slug:slug>/history/', views.article_history, name='article-history'),
    path('articles/<slug:slug>/revision/<int:revision_id>/', views.article_revision, name='article-revision'),
    path('articles/<slug:slug>/compare/', views.article_compare, name='article-compare'),
    path('articles/<slug:slug>/delete/', views.article_delete, name='article-delete'),
    
    # Category URLs
    path('categories/', views.category_list, name='categories'),
    path('categories/<slug:slug>/', views.category_articles, name='article-category'),
    
    # Tag URLs
    path('tags/', views.tag_list, name='article-tags'),
    path('tags/<slug:slug>/', views.tag_articles, name='article-tag'),
    
    # SEO-Optimized URL Patterns for Northeast India Content (Basic Implementation)
    
    # Category-State specific URLs (SEO optimized) - Main benefit achieved
    path('personalities/<slug:state_slug>/<slug:slug>/', views.article_detail, name='seo-personalities-detail'),
    path('culture/<slug:state_slug>/<slug:slug>/', views.article_detail, name='seo-culture-detail'),
    path('festivals/<slug:state_slug>/<slug:slug>/', views.article_detail, name='seo-festivals-detail'),
    path('places/<slug:state_slug>/<slug:slug>/', views.article_detail, name='seo-places-detail'),
    path('heritage/<slug:state_slug>/<slug:slug>/', views.article_detail, name='seo-heritage-detail'),
]
