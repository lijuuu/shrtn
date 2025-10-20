"""
URL patterns for user management endpoints.
"""
from django.urls import path
from .views import UserView
from . import auth_views

# Create view instance
user_view = UserView()

urlpatterns = [
    # User management endpoints
    path('', user_view.list_users, name='user-list'),
    path('search/', user_view.search_users, name='user-search'),
    
    # Authentication endpoints
    path('google-login/', user_view.google_login, name='google-login'),
    
    # Profile management endpoints
    path('profile/', auth_views.get_profile, name='get-profile'),
    path('update-profile/', auth_views.update_profile, name='update-profile'),
]
