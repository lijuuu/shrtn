from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

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
    
    # API endpoints
    path("api/", include("users.urls")),
    path("api/", include("organizations.urls")),
    path("api/", include("namespaces.urls")),
    path("api/", include("urls.urls")),
    
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # Debug toolbar for development
    if "debug_toolbar" in settings.INSTALLED_APPS:
        from django.urls import include
        import debug_toolbar
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
