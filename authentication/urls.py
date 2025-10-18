"""
Authentication URL patterns.
"""
from django.urls import path
from . import views

urlpatterns = [
    # User registration and login
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    
    # Google OAuth
    path('google/login/', views.google_login, name='google-login'),
    path('google/callback/', views.google_callback, name='google-callback'),
    
    # Authentication status and token management
    path('status/', views.auth_status, name='auth-status'),
    path('refresh/', views.refresh_token, name='refresh-token'),
    
    # User profile management
    path('change-password/', views.change_password, name='change-password'),
    path('update-profile/', views.update_profile, name='update-profile'),
]