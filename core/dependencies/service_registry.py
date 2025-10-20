"""
centralized service registry for application-level initialization.
"""
import logging
from typing import Dict, Any, Optional
from core.dependencies.database import db_dependency

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """centralized service registry with application-level initialization."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False
    
    def initialize_all_services(self) -> None:
        """initialize all services at application startup."""
        if self._initialized:
            return
        
        try:
            logger.info("initializing all services...")
            
            #initialize postgresql connection (required)
            postgres = db_dependency.get_postgres()
            
            #initialize redis connection (required for caching)
            redis = db_dependency.get_redis()
            
            #initialize user service (postgresql only)
            self._initialize_user_service(postgres)
            
            #initialize organization service (postgresql only)
            self._initialize_organization_service(postgres)
            
            #initialize namespace service (postgresql only)
            self._initialize_namespace_service(postgres)
            
            
            #initialize email service (optional)
            self._initialize_email_service()
            
            #try to initialize scylladb connection (optional for startup)
            try:
                scylla = db_dependency.get_scylla()
                self._initialize_url_service(scylla)
                self._initialize_analytics_service(scylla)
                logger.info("scylladb service initialized successfully")
            except Exception as scylla_error:
                logger.warning("scylladb not available during startup: %s", scylla_error)
                logger.info("url service will be initialized on first use")
                #don't fail startup if scylladb is not ready
            
            self._initialized = True
            logger.info("core services initialized successfully")
            
        except Exception as e:
            logger.error("failed to initialize core services: %s", e)
            #don't raise here to avoid breaking django startup
            logger.warning("services will be initialized on first use")
    
    def _initialize_user_service(self, postgres) -> None:
        """initialize user service."""
        try:
            from users.services import UserService
            from users.repositories import UserRepository
            
            user_repository = UserRepository(postgres)
            self._services['user'] = UserService(user_repository)
            logger.info("user service initialized")
            
        except Exception as e:
            logger.error("failed to initialize user service: %s", e)
            raise
    
    def _initialize_organization_service(self, postgres) -> None:
        """initialize organization service."""
        try:
            from organizations.services import OrganizationService
            from organizations.repositories import OrganizationRepository
            
            org_repository = OrganizationRepository(postgres)
            self._services['organization'] = OrganizationService(org_repository)
            logger.info("organization service initialized")
            
        except Exception as e:
            logger.error("failed to initialize organization service: %s", e)
            raise
    
    def _initialize_namespace_service(self, postgres) -> None:
        """initialize namespace service."""
        try:
            from namespaces.services import NamespaceService
            from namespaces.repositories import NamespaceRepository
            
            namespace_repository = NamespaceRepository(postgres)
            self._services['namespace'] = NamespaceService(namespace_repository)
            logger.info("namespace service initialized")
            
        except Exception as e:
            logger.error("failed to initialize namespace service: %s", e)
            raise
    
    
    def _initialize_url_service(self, scylla) -> None:
        """initialize url service."""
        try:
            from urls.services import UrlService
            from urls.repositories import UrlRepository
            
            url_repository = UrlRepository(scylla)
            self._services['url'] = UrlService(url_repository)
            logger.info("url service initialized")
            
        except Exception as e:
            logger.error("failed to initialize url service: %s", e)
            raise
    
    def _initialize_email_service(self) -> None:
        """initialize email service."""
        try:
            from core.email.smtp_service import SMTPEmailService
            
            self._services['email'] = SMTPEmailService()
            logger.info("email service initialized")
            
        except Exception as e:
            logger.error("failed to initialize email service: %s", e)
            # Don't raise - email service is optional
    
    def _initialize_analytics_service(self, scylla) -> None:
        """initialize analytics service."""
        try:
            from analytics.analytics_service import AnalyticsService
            
            self._services['analytics'] = AnalyticsService(scylla)
            logger.info("analytics service initialized")
            
        except Exception as e:
            logger.error("failed to initialize analytics service: %s", e)
            # Don't raise - analytics service is optional
    
    def get_user_service(self):
        """get user service."""
        if not self._initialized:
            self.initialize_all_services()
        return self._services['user']
    
    def get_organization_service(self):
        """get organization service."""
        if not self._initialized:
            self.initialize_all_services()
        return self._services['organization']
    
    def get_namespace_service(self):
        """get namespace service."""
        if not self._initialized:
            self.initialize_all_services()
        return self._services['namespace']
    
    
    def get_email_service(self):
        """get email service."""
        if not self._initialized:
            self.initialize_all_services()
        return self._services.get('email')
    
    def get_analytics_service(self):
        """get analytics service."""
        if not self._initialized:
            self.initialize_all_services()
        return self._services.get('analytics')
    
    def get_url_service(self):
        """get url service."""
        if not self._initialized:
            self.initialize_all_services()
        
        #if url service wasn't initialized at startup, try to initialize it now
        if 'url' not in self._services:
            try:
                scylla = db_dependency.get_scylla()
                self._initialize_url_service(scylla)
                logger.info("url service initialized on first use")
            except Exception as e:
                logger.error("failed to initialize url service: %s", e)
                raise
        
        return self._services['url']
    
    def is_initialized(self) -> bool:
        """check if services are initialized."""
        return self._initialized
    
    def reset(self) -> None:
        """reset service registry (for testing)."""
        self._services.clear()
        self._initialized = False


#global service registry instance
service_registry = ServiceRegistry()
