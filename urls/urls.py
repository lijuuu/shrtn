"""
URL patterns for URL endpoints.
"""
from django.urls import path
from .views import UrlView

# Create view instance
url_view = UrlView()

urlpatterns = [
    # URL Management
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/', url_view.list_urls, name='url-list'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/create/', url_view.create_url, name='url-create'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/', url_view.get_url, name='url-detail'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/update/', url_view.update_url, name='url-update'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/delete/', url_view.delete_url, name='url-delete'),
    
    # URL Resolution (public)
    path('<str:namespace>/<str:shortcode>/', url_view.resolve_url, name='url-resolve'),
    
    # Bulk URL Operations
    path('organizations/<int:org_id>/namespaces/<str:namespace>/urls/bulk/', url_view.bulk_create_urls, name='url-bulk-create'),
    
    # Cache Management
    path('cache/hot-urls/', url_view.get_hot_urls, name='cache-hot-urls'),
    path('cache/stats/', url_view.get_cache_stats, name='cache-stats'),
    path('cache/clear/', url_view.clear_cache, name='cache-clear'),
    path('cache/test/', url_view.test_cache, name='cache-test'),
    
    # Analytics
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/analytics/', url_view.get_url_analytics, name='url-analytics'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/analytics/', url_view.get_namespace_analytics, name='namespace-analytics'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/analytics/realtime/', url_view.get_realtime_stats, name='realtime-stats'),
]
