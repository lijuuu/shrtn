"""
core app configuration.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """core app configuration with startup initialization."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self) -> None:
        """initialize services when django app is ready."""
        try:
            from core.dependencies.service_registry import service_registry
            from core.dependencies.database import db_dependency
            
            #initialize database connections first
            db_dependency.initialize_connections()
            
            #then initialize all services
            service_registry.initialize_all_services()
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("failed to initialize services on app ready: %s", e)
            #don't raise here to avoid breaking django startup
