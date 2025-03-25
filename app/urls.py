from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'app'  # Define namespace for URL names

urlpatterns = [
    path('', views.home, name='home'),
    
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
    
    # Article URLs
    path('articles/', views.article_list, name='article-list'),
    path('articles/create/', views.article_create, name='article-create'),
    path('articles/<slug:slug>/', views.article_detail, name='article-detail'),
    path('articles/<slug:slug>/edit/', views.article_edit, name='article-edit'),
    path('articles/<slug:slug>/history/', views.article_history, name='article-history'),
    path('articles/<slug:slug>/revision/<int:revision_id>/', views.article_revision, name='article-revision'),
    path('articles/<slug:slug>/compare/', views.article_compare, name='article-compare'),
    
    # Category URLs
    path('categories/', views.category_list, name='categories'),
    path('categories/<slug:slug>/', views.category_articles, name='article-category'),
    
    # Tag URLs
    path('tags/', views.tag_list, name='article-tags'),
    path('tags/<slug:slug>/', views.tag_articles, name='article-tag'),
]
