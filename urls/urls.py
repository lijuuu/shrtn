"""
URL patterns for URL endpoints.
"""
from django.urls import path
from .views import UrlView

# Create view instance
url_view = UrlView()

urlpatterns = [
    # URL Management
    path('organizations/<int:org_id>/namespaces/<str:namespace>/urls/', url_view.list_urls, name='url-list'),
    path('organizations/<int:org_id>/namespaces/<str:namespace>/urls/create/', url_view.create_url, name='url-create'),
    path('organizations/<int:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/', url_view.get_url, name='url-detail'),
    path('organizations/<int:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/update/', url_view.update_url, name='url-update'),
    path('organizations/<int:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/delete/', url_view.delete_url, name='url-delete'),
    
    # URL Resolution (public)
    path('<str:namespace>/<str:shortcode>/', url_view.resolve_url, name='url-resolve'),
    
    # Bulk URL Operations
    path('organizations/<int:org_id>/namespaces/<str:namespace>/urls/bulk/', url_view.bulk_create_urls, name='url-bulk-create'),
]
