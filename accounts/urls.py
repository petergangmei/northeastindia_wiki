from django.urls import path
from . import views

app_name = 'accounts'  # Define namespace for URL names

urlpatterns = [
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
]