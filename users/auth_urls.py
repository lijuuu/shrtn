"""
URL patterns for authentication endpoints.
"""
from django.urls import path
from . import auth_views
from .views import UserView

# Create view instance for Google OAuth
user_view = UserView()

urlpatterns = [
    # Authentication endpoints
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('change-password/', auth_views.change_password, name='change-password'),
    path('status/', auth_views.auth_status, name='auth-status'),
    
    # Google OAuth endpoints
    path('google/login/', user_view.google_login, name='google-login'),
    path('google/callback/', user_view.google_callback, name='google-callback'),
    path('google/login/api/', user_view.google_login_api, name='google-login-api'),
]
