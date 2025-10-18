"""
Namespace service for business logic.
"""
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
        
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        
        if not created_by_user_id or created_by_user_id <= 0:
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

    def get_by_id(self, namespace_id: int) -> Optional[Namespace]:
        """Get namespace by ID."""
        if not namespace_id or namespace_id <= 0:
            raise ValidationError("Invalid namespace ID")
        return self.repository.get_by_id(namespace_id)

    def get_by_name(self, name: str) -> Optional[Namespace]:
        """Get namespace by name."""
        if not name or len(name.strip()) < 2:
            raise ValidationError("Invalid namespace name")
        return self.repository.get_by_name(name.strip().lower())

    def update(self, namespace_id: int, data: Dict[str, Any]) -> Optional[Namespace]:
        """Update namespace."""
        if not namespace_id or namespace_id <= 0:
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
            
            data['name'] = name.strip().lower()
        
        return self.repository.update(namespace_id, data)

    def delete(self, namespace_id: int) -> bool:
        """Delete namespace."""
        if not namespace_id or namespace_id <= 0:
            raise ValidationError("Invalid namespace ID")
        return self.repository.delete(namespace_id)

    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Namespace]:
        """List namespaces with optional filters."""
        return self.repository.list(filters)

    def get_by_organization(self, org_id: int) -> List[Namespace]:
        """Get namespaces by organization."""
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        return self.repository.get_by_organization(org_id)

    def get_by_creator(self, user_id: int) -> List[Namespace]:
        """Get namespaces created by user."""
        if not user_id or user_id <= 0:
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
