"""
URL patterns for user endpoints.
"""
from django.urls import path
from .views import UserView

# Create view instance
user_view = UserView()

urlpatterns = [
    # User CRUD operations
    path('users/', user_view.list_users, name='user-list'),
    path('users/create/', user_view.create_user, name='user-create'),
    path('users/<int:user_id>/', user_view.get_user, name='user-detail'),
    path('users/<int:user_id>/update/', user_view.update_user, name='user-update'),
    path('users/<int:user_id>/delete/', user_view.delete_user, name='user-delete'),
    path('users/<int:user_id>/stats/', user_view.get_user_stats, name='user-stats'),
    
    # User search and lookup
    path('users/email/<str:email>/', user_view.get_user_by_email, name='user-by-email'),
    path('users/search/', user_view.search_users, name='user-search'),
]
