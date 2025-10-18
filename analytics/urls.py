"""
URL patterns for analytics endpoints.
"""
from django.urls import path
from .views import AnalyticsView

# Create view instance
analytics_view = AnalyticsView()

urlpatterns = [
    # URL Analytics
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/urls/<str:shortcode>/analytics/', 
         analytics_view.get_url_analytics, name='url-analytics'),
    
    # Namespace Analytics
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/analytics/', 
         analytics_view.get_namespace_analytics, name='namespace-analytics'),
    
    # Real-time Statistics
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/analytics/realtime/', 
         analytics_view.get_realtime_stats, name='realtime-stats'),
    
    # Country Analytics
    path('organizations/<uuid:org_id>/analytics/countries/', 
         analytics_view.get_country_analytics, name='country-analytics'),
    
    # Tier Analytics
    path('organizations/<uuid:org_id>/analytics/tiers/', 
         analytics_view.get_tier_analytics, name='tier-analytics'),
]
