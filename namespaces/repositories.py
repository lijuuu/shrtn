"""
Namespace repository for PostgreSQL operations.
"""
import uuid
import logging
from typing import List, Optional, Dict, Any
from core.database.base import Repository
from core.database.postgres import PostgreSQLConnection
from .models import Namespace

logger = logging.getLogger(__name__)


class NamespaceRepository(Repository):
    """Repository for Namespace operations using PostgreSQL."""
    
    def __init__(self, connection: PostgreSQLConnection):
        super().__init__(connection)
        self.postgres = connection
    
    def create(self, data: Dict[str, Any]) -> Namespace:
        """Create a new namespace."""
        try:
            namespace = Namespace.objects.create(
                organization_id=data['org_id'],
                created_by_id=data['created_by_user_id'],
                name=data['name']
            )
            logger.info("Created namespace: %s", namespace.name)
            return namespace
        except Exception as e:
            logger.error("Failed to create namespace: %s", e)
            raise
    
    def get_by_id(self, namespace_id: uuid.UUID) -> Optional[Namespace]:
        """Get namespace by ID."""
        try:
            return Namespace.objects.get(namespace_id=namespace_id)
        except Namespace.DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get namespace by ID: %s", e)
            raise
    
    def get_by_name(self, name: str) -> Optional[Namespace]:
        """Get namespace by name."""
        try:
            return Namespace.objects.get(name=name)
        except Namespace.DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get namespace by name: %s", e)
            raise
    
    def update(self, namespace_id: uuid.UUID, data: Dict[str, Any]) -> Optional[Namespace]:
        """Update namespace."""
        try:
            namespace = self.get_by_id(namespace_id)
            if not namespace:
                return None
            
            for field, value in data.items():
                if hasattr(namespace, field):
                    setattr(namespace, field, value)
            
            namespace.save()
            logger.info("Updated namespace: %s", namespace.name)
            return namespace
        except Exception as e:
            logger.error("Failed to update namespace: %s", e)
            raise
    
    def delete(self, namespace_id: uuid.UUID) -> bool:
        """Delete namespace."""
        try:
            namespace = self.get_by_id(namespace_id)
            if not namespace:
                return False
            
            namespace.delete()
            logger.info("Deleted namespace: %s", namespace.name)
            return True
        except Exception as e:
            logger.error("Failed to delete namespace: %s", e)
            raise
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Namespace]:
        """List namespaces with optional filters."""
        try:
            queryset = Namespace.objects.all()
            
            if filters:
                if 'org_id' in filters:
                    queryset = queryset.filter(organization_id=filters['org_id'])
                if 'created_by_user_id' in filters:
                    queryset = queryset.filter(created_by_id=filters['created_by_user_id'])
            
            return list(queryset)
        except Exception as e:
            logger.error("Failed to list namespaces: %s", e)
            raise
    
    def check_name_availability(self, name: str) -> bool:
        """Check if namespace name is available."""
        try:
            return not Namespace.objects.filter(name=name).exists()
        except Exception as e:
            logger.error("Failed to check name availability: %s", e)
            raise
    
    def get_by_organization(self, org_id: uuid.UUID) -> List[Namespace]:
        """Get namespaces by organization."""
        try:
            return list(Namespace.objects.filter(organization_id=org_id))
        except Exception as e:
            logger.error("Failed to get namespaces by organization: %s", e)
            raise
    
    def get_by_creator(self, user_id: uuid.UUID) -> List[Namespace]:
        """Get namespaces created by user."""
        try:
            return list(Namespace.objects.filter(created_by_id=user_id))
        except Exception as e:
            logger.error("Failed to get namespaces by creator: %s", e)
            raise
