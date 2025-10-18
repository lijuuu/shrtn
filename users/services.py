"""
User service for business logic.
"""
import uuid
from typing import Optional, List, Dict, Any
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from core.database.base import Service
from .repositories import UserRepository

User = get_user_model()


class UserService(Service):
    """
    Service layer for User business logic.
    """
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.repository = repository

    def create(self, data: Dict[str, Any]) -> User:
        """Create user with business logic validation."""
        email = data.get('email', '')
        password = data.get('password', '')
        name = data.get('name', '')
        verified = data.get('verified', False)
        
        if not email or '@' not in email:
            raise ValidationError("Invalid email format")
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        # Check if user already exists
        if self.repository.get_by_email(email):
            raise ValidationError("User with this email already exists")
        
        return self.repository.create({
            'email': email,
            'password': password,
            'name': name,
            'verified': verified
        })

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID with validation."""
        if not user_id:
            raise ValidationError("Invalid user ID")
        return self.repository.get_by_id(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email with validation."""
        if not email or '@' not in email:
            raise ValidationError("Invalid email format")
        return self.repository.get_by_email(email)

    def update(self, user_id: uuid.UUID, data: Dict[str, Any]) -> Optional[User]:
        """Update user with validation."""
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        # Validate email if provided
        if 'email' in data:
            email = data['email']
            if not email or '@' not in email:
                raise ValidationError("Invalid email format")
            
            # Check if email is already taken by another user
            existing_user = self.repository.get_by_email(email)
            if existing_user and existing_user.id != user_id:
                raise ValidationError("Email already taken by another user")
        
        return self.repository.update(user_id, data)

    def delete(self, user_id: uuid.UUID) -> bool:
        """Delete user with cascade delete for created content."""
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        try:
            # Get user info before deletion
            user = self.repository.get_by_id(user_id)
            if not user:
                return False
            
            # Get services to handle cascade deletion
            from core.dependencies.service_registry import service_registry
            organization_service = service_registry.get_organization_service()
            namespace_service = service_registry.get_namespace_service()
            
            # Delete organizations owned by user
            try:
                user_orgs = organization_service.get_user_organizations(user_id)
                for org in user_orgs:
                    # This will cascade delete all namespaces and URLs
                    organization_service.delete(org.org_id)
                    logger.info("Deleted organization %s owned by user %s", org.name, user.email)
            except Exception as org_error:
                logger.warning("Failed to delete organizations for user %s: %s", user.email, org_error)
            
            # Delete namespaces created by user
            try:
                user_namespaces = namespace_service.get_by_creator(user_id)
                for namespace in user_namespaces:
                    # This will cascade delete all URLs in the namespace
                    namespace_service.delete(namespace.namespace_id)
                    logger.info("Deleted namespace %s created by user %s", namespace.name, user.email)
            except Exception as namespace_error:
                logger.warning("Failed to delete namespaces for user %s: %s", user.email, namespace_error)
            
            # Delete user from PostgreSQL
            success = self.repository.delete(user_id)
            
            if success:
                logger.info("Deleted user %s and all associated content", user.email)
            
            return success
            
        except Exception as e:
            logger.error("Failed to delete user: %s", e)
            raise

    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[User]:
        """List users with optional filtering."""
        return self.repository.list(filters)

    def search_users(self, query: str) -> List[User]:
        """Search users by name."""
        if not query or len(query.strip()) < 2:
            raise ValidationError("Search query must be at least 2 characters")
        return self.repository.search_by_name(query.strip())

    def get_user_stats(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Get user statistics."""
        if not user_id:
            raise ValidationError("Invalid user ID")
        return self.repository.get_user_stats(user_id)