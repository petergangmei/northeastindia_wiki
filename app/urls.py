from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'app'  # Define namespace for URL names

urlpatterns = [
    path('', views.home, name='home'),
    
    # SEO and crawlers
    path('robots.txt', views.robots_txt, name='robots-txt'),
    
    
    # Notification URLs
    path('notifications/', views.notification_list, name='notification-list'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete-notification'),
    path('notifications/delete-all-read/', views.delete_all_notifications, name='delete-all-notifications'),
    
    # Article URLs
    path('wiki/', views.article_list, name='article-list'),
    path('wiki/search/', views.article_search, name='article-search'),
    path('wiki/search-htmx/', views.article_search_htmx, name='article-search-htmx'),
    path('wiki/create/', views.article_create, name='article-create'),
    
    # Article Review - Place review URLs before article detail to avoid URL conflicts
    path('wiki/review-queue/', views.article_review_queue, name='article-review-queue'),
    path('wiki/<slug:slug>/review/', views.article_review, name='article-review'),
    path('wiki/<slug:slug>/review/action/', views.article_review_action, name='article-review-action'),
    
    # Revision Review URLs
    path('revision/<int:revision_id>/review/', views.revision_review, name='revision-review'),
    path('revision/<int:revision_id>/review/action/', views.revision_review_action, name='revision-review-action'),
    
    # Article detail and related URLs
    path('wiki/<slug:slug>/', views.article_detail, name='article-detail'),
    path('wiki/<slug:slug>/edit/', views.article_edit, name='article-edit'),
    path('wiki/<slug:slug>/history/', views.article_history, name='article-history'),
    path('wiki/<slug:slug>/revision/<int:revision_id>/', views.article_revision, name='article-revision'),
    path('wiki/<slug:slug>/compare/', views.article_compare, name='article-compare'),
    path('wiki/<slug:slug>/delete/', views.article_delete, name='article-delete'),
    
    # Category-specific list URLs (placed BEFORE general patterns to avoid conflicts)
    path('personalities/', views.personalities_list, name='personalities-list'),
    path('culture/', views.culture_list, name='culture-list'),
    path('festivals/', views.festivals_list, name='festivals-list'),
    path('places/', views.places_list, name='places-list'),
    path('tribal-culture/', views.tribal_culture_list, name='tribal-culture-list'),
    
    # SEO-Optimized URL Patterns for Northeast India Content (Basic Implementation)
    
    # Category-State specific URLs (SEO optimized) - Main benefit achieved
    path('personalities/<slug:state_slug>/<slug:slug>/', views.article_detail, name='seo-personalities-detail'),
    path('culture/<slug:state_slug>/<slug:slug>/', views.article_detail, name='seo-culture-detail'),
    path('festivals/<slug:state_slug>/<slug:slug>/', views.article_detail, name='seo-festivals-detail'),
    path('places/<slug:state_slug>/<slug:slug>/', views.article_detail, name='seo-places-detail'),
    path('heritage/<slug:state_slug>/<slug:slug>/', views.article_detail, name='seo-heritage-detail'),
    
    # Category URLs
    path('categories/', views.category_list, name='categories'),
    path('categories/<slug:slug>/', views.category_articles, name='article-category'),
    
    # Tag URLs
    path('tags/', views.tag_list, name='article-tags'),
    path('tags/<slug:slug>/', views.tag_articles, name='article-tag'),
    
    # State URLs
    path('states/', views.state_list, name='state-list'),
    path('states/<slug:state_slug>/', views.state_detail, name='state-detail'),
    path('states/<slug:state_slug>/culture/', views.state_category_articles, {'category_slug': 'culture'}, name='state-culture-articles'),
    path('states/<slug:state_slug>/places/', views.state_category_articles, {'category_slug': 'places'}, name='state-places-articles'),
]
