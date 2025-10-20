"""
URL patterns for URL endpoints.
"""
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import UrlView
from .error_views import url_not_found, url_inactive, url_expired, server_error

# Create view instance
url_view = UrlView()

urlpatterns = [
    # URL Management
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/', url_view.list_urls, name='url-list'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/create/', url_view.create_url, name='url-create'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/', url_view.get_url, name='url-detail'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/update/', url_view.update_url, name='url-update'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/delete/', url_view.delete_url, name='url-delete'),
    
    
    # Bulk URL Operations
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/bulk/', csrf_exempt(url_view.bulk_create_urls), name='url-bulk-create'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/bulk/excel/', url_view.bulk_upload_excel, name='url-bulk-excel'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/template/', url_view.get_excel_template, name='url-excel-template'),
    
    # URL Resolution (public) - dedicated endpoint
    path('urls/resolve/<str:namespace>/<str:shortcode>/', url_view.resolve_url, name='url-resolve-api'),
    
    # Public Analytics (no auth required)
    path('urls/<str:namespace>/<str:shortcode>/stats/', url_view.get_public_analytics, name='url-public-stats'),
    
    # URL Resolution (public) - must come last to avoid conflicts
    path('<str:namespace>/<str:shortcode>/', url_view.resolve_url, name='url-resolve'),
    
    # Analytics
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/analytics/', url_view.get_url_analytics, name='url-analytics'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/stats/', url_view.get_simple_analytics, name='url-simple-analytics'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/analytics/', url_view.get_namespace_analytics, name='namespace-analytics'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/analytics/realtime/', url_view.get_realtime_stats, name='realtime-stats'),
    
    # Error pages for URL redirection
    path('404/', url_not_found, name='url-404'),
    path('inactive/', url_inactive, name='url-inactive'),
    path('expired/', url_expired, name='url-expired'),
    path('500/', server_error, name='url-500'),
]
