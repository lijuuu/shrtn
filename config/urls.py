from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from config.health import (
    health_check,
    health_detailed,
    health_ready,
    health_live,
)

# Customize admin site
admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.site_title = settings.ADMIN_SITE_TITLE
admin.site.index_title = settings.ADMIN_INDEX_TITLE

urlpatterns = [
    # Health check endpoints
    path("health/", health_check, name="health"),
    path("health/detailed/", health_detailed, name="health-detailed"),
    path("health/ready/", health_ready, name="health-ready"),
    path("health/live/", health_live, name="health-live"),
    
    # Authentication endpoints 
    path("auth/", include("users.auth_urls")),
    
    # API endpoints - Version 1
    path("api/v1/users/", include("users.urls")),
    path("api/v1/organizations/", include("organizations.urls")),
    path("api/v1/", include("namespaces.urls")),
    path("api/v1/", include("urls.urls")),
    path("api/v1/", include("analytics.urls")),
    
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # Debug toolbar for development
    if "debug_toolbar" in settings.INSTALLED_APPS:
        from django.urls import include
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
