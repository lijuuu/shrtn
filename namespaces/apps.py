"""
Namespaces app configuration.
"""
from django.apps import AppConfig


class NamespacesConfig(AppConfig):
    """Namespaces app configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'namespaces'
    verbose_name = 'Namespace Management'
