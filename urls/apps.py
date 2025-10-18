"""
URLs app configuration.
"""
from django.apps import AppConfig


class UrlsConfig(AppConfig):
    """URLs app configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'urls'
    verbose_name = 'URL Management'
