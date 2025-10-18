"""
Namespace service for business logic.
"""
import uuid
import logging
from typing import Optional, List, Dict, Any
from django.core.exceptions import ValidationError
from core.database.base import Service
from .repositories import NamespaceRepository
from .models import Namespace

logger = logging.getLogger(__name__)


class NamespaceService(Service):
    """
    Service layer for Namespace business logic.
    """
    def __init__(self, repository: NamespaceRepository):
        super().__init__(repository)
        self.repository = repository

    def create(self, data: Dict[str, Any]) -> Namespace:
        """Create namespace with business logic validation."""
        name = data.get('name', '')
        org_id = data.get('org_id')
        created_by_user_id = data.get('created_by_user_id')
        
        if not name or len(name.strip()) < 2:
            raise ValidationError("Namespace name must be at least 2 characters")
        
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        if not created_by_user_id:
            raise ValidationError("Invalid user ID")
        
        # Check if namespace name is available globally
        if not self.repository.check_name_availability(name.strip()):
            raise ValidationError("Namespace name is already taken")
        
        # Validate namespace name format (alphanumeric, hyphens, underscores only)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', name.strip()):
            raise ValidationError("Namespace name can only contain letters, numbers, hyphens, and underscores")
        
        return self.repository.create({
            'name': name.strip().lower(),
            'org_id': org_id,
            'created_by_user_id': created_by_user_id
        })

    def get_by_id(self, namespace_id: uuid.UUID) -> Optional[Namespace]:
        """Get namespace by ID."""
        if not namespace_id:
            raise ValidationError("Invalid namespace ID")
        return self.repository.get_by_id(namespace_id)

    def get_by_name(self, name: str) -> Optional[Namespace]:
        """Get namespace by name."""
        if not name or len(name.strip()) < 2:
            raise ValidationError("Invalid namespace name")
        return self.repository.get_by_name(name.strip().lower())

    def update(self, namespace_id: uuid.UUID, data: Dict[str, Any]) -> Optional[Namespace]:
        """Update namespace with shortcode table updates."""
        if not namespace_id:
            raise ValidationError("Invalid namespace ID")
        
        if 'name' in data:
            name = data['name']
            if not name or len(name.strip()) < 2:
                raise ValidationError("Namespace name must be at least 2 characters")
            
            # Check if new name is available
            if not self.repository.check_name_availability(name.strip()):
                raise ValidationError("Namespace name is already taken")
            
            # Validate namespace name format
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', name.strip()):
                raise ValidationError("Namespace name can only contain letters, numbers, hyphens, and underscores")
            
            # Get current namespace to check if name is actually changing
            current_namespace = self.repository.get_by_id(namespace_id)
            if current_namespace and current_namespace.name != name.strip().lower():
                # Name is changing - we need to update shortcode table references
                old_name = current_namespace.name
                new_name = name.strip().lower()
                
                # Update shortcode table to reflect new namespace name
                try:
                    from core.dependencies.service_registry import service_registry
                    url_service = service_registry.get_url_service()
                    
                    # Migrate all URLs from old namespace name to new namespace name
                    migration_success = url_service.migrate_namespace_name(old_name, new_name)
                    
                    if migration_success:
                        logger.info("Successfully migrated URLs from namespace %s to %s", old_name, new_name)
                    else:
                        logger.warning("Failed to migrate URLs from namespace %s to %s", old_name, new_name)
                        
                except Exception as url_error:
                    logger.warning("Failed to update URLs for namespace rename: %s", url_error)
                    # Continue with namespace update even if URL update fails
            
            data['name'] = name.strip().lower()
        
        return self.repository.update(namespace_id, data)

    def delete(self, namespace_id: uuid.UUID) -> bool:
        """Delete namespace with cascade delete for URLs."""
        if not namespace_id:
            raise ValidationError("Invalid namespace ID")
        
        try:
            # Get namespace info before deletion
            namespace = self.repository.get_by_id(namespace_id)
            if not namespace:
                return False
            
            # Get URL service to handle cascade deletion
            from core.dependencies.service_registry import service_registry
            url_service = service_registry.get_url_service()
            
            # Delete all URLs in this namespace
            try:
                urls_in_namespace = url_service.get_by_namespace(namespace_id)
                for url in urls_in_namespace:
                    # Delete from ScyllaDB
                    url_service.delete((namespace_id, url.shortcode))
                    logger.info("Deleted URL %s from namespace %s", url.shortcode, namespace.name)
            except Exception as url_error:
                logger.warning("Failed to delete URLs for namespace %s: %s", namespace.name, url_error)
                # Continue with namespace deletion even if URL deletion fails
            
            # Delete namespace from PostgreSQL
            success = self.repository.delete(namespace_id)
            
            if success:
                logger.info("Deleted namespace %s and all associated URLs", namespace.name)
            
            return success
            
        except Exception as e:
            logger.error("Failed to delete namespace: %s", e)
            raise

    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Namespace]:
        """List namespaces with optional filters."""
        return self.repository.list(filters)

    def get_by_organization(self, org_id: uuid.UUID) -> List[Namespace]:
        """Get namespaces by organization."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        return self.repository.get_by_organization(org_id)

    def get_by_creator(self, user_id: uuid.UUID) -> List[Namespace]:
        """Get namespaces created by user."""
        if not user_id:
            raise ValidationError("Invalid user ID")
        return self.repository.get_by_creator(user_id)

    def check_name_availability(self, name: str) -> bool:
        """Check if namespace name is available."""
        if not name or len(name.strip()) < 2:
            raise ValidationError("Invalid namespace name")
        
        # Validate namespace name format
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', name.strip()):
            raise ValidationError("Namespace name can only contain letters, numbers, hyphens, and underscores")
        
        return self.repository.check_name_availability(name.strip().lower())
