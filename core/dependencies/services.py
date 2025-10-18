"""
Service dependency injection container.
"""
import logging
from typing import Optional
from core.dependencies.database import db_dependency

logger = logging.getLogger(__name__)


class ServiceDependency:
    """Service dependency injection container."""
    
    def __init__(self):
        self._user_service = None
        self._org_service = None
        self._namespace_service = None
        self._url_service = None
    
    def get_user_service(self):
        """Get User service."""
        if self._user_service is None:
            try:
                from users.services import UserService
                from users.repositories import UserRepository
                
                # Create repository with PostgreSQL connection
                postgres = db_dependency.get_postgres()
                user_repository = UserRepository(postgres)
                
                # Create service with repository
                self._user_service = UserService(user_repository)
                logger.info("User service initialized")
            except Exception as e:
                logger.error("Failed to initialize User service: %s", e)
                raise
        return self._user_service
    
    def get_organization_service(self):
        """Get Organization service."""
        if self._org_service is None:
            try:
                from organizations.services import OrganizationService
                from organizations.repositories import OrganizationRepository
                
                # Create repository with PostgreSQL connection
                postgres = db_dependency.get_postgres()
                org_repository = OrganizationRepository(postgres)
                
                # Create service with repository
                self._org_service = OrganizationService(org_repository)
                logger.info("Organization service initialized")
            except Exception as e:
                logger.error("Failed to initialize Organization service: %s", e)
                raise
        return self._org_service
    
    def get_namespace_service(self):
        """Get Namespace service."""
        if self._namespace_service is None:
            try:
                from namespaces.services import NamespaceService
                from namespaces.repositories import NamespaceRepository
                
                # Create repository with PostgreSQL connection
                postgres = db_dependency.get_postgres()
                namespace_repository = NamespaceRepository(postgres)
                
                # Create service with repository
                self._namespace_service = NamespaceService(namespace_repository)
                logger.info("Namespace service initialized")
            except Exception as e:
                logger.error("Failed to initialize Namespace service: %s", e)
                raise
        return self._namespace_service
    
    def get_url_service(self):
        """Get URL service."""
        if self._url_service is None:
            try:
                from urls.services import UrlService
                from urls.repositories import UrlRepository
                
                # Create repository with ScyllaDB connection
                scylla = db_dependency.get_scylla()
                url_repository = UrlRepository(scylla)
                
                # Create service with repository
                self._url_service = UrlService(url_repository)
                logger.info("URL service initialized")
            except Exception as e:
                logger.error("Failed to initialize URL service: %s", e)
                raise
        return self._url_service


# Global service dependency instance
service_dependency = ServiceDependency()
