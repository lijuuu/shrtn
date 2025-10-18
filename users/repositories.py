"""
User repository for PostgreSQL operations.
"""
import logging
from typing import List, Optional, Dict, Any
from django.contrib.auth import get_user_model
from core.database.base import Repository
from core.database.postgres import PostgreSQLConnection

logger = logging.getLogger(__name__)
User = get_user_model()


class UserRepository(Repository):
    """Repository for User operations using PostgreSQL."""
    
    def __init__(self, connection: PostgreSQLConnection):
        super().__init__(connection)
        self.postgres = connection
    
    def create(self, data: Dict[str, Any]) -> User:
        """Create a new user."""
        try:
            user = User.objects.create_user(
                email=data['email'],
                username=data.get('username', ''),
                name=data.get('name', ''),
                password=data['password'],
                verified=data.get('verified', False)
            )
            logger.info("Created user: %s", user.email)
            return user
        except Exception as e:
            logger.error("Failed to create user: %s", e)
            raise
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get user by ID: %s", e)
            raise
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get user by email: %s", e)
            raise
    
    def update(self, user_id: int, data: Dict[str, Any]) -> Optional[User]:
        """Update user."""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return None
            
            for field, value in data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.save()
            logger.info("Updated user: %s", user.email)
            return user
        except Exception as e:
            logger.error("Failed to update user: %s", e)
            raise
    
    def delete(self, user_id: int) -> bool:
        """Delete user."""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
            
            user.delete()
            logger.info("Deleted user: %s", user.email)
            return True
        except Exception as e:
            logger.error("Failed to delete user: %s", e)
            raise
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[User]:
        """List users with optional filters."""
        try:
            queryset = User.objects.all()
            
            if filters:
                if 'verified_only' in filters and filters['verified_only']:
                    queryset = queryset.filter(verified=True)
                if 'is_active' in filters:
                    queryset = queryset.filter(is_active=filters['is_active'])
            
            return list(queryset)
        except Exception as e:
            logger.error("Failed to list users: %s", e)
            raise
    
    def search_by_name(self, query: str) -> List[User]:
        """Search users by name."""
        try:
            return list(User.objects.filter(name__icontains=query))
        except Exception as e:
            logger.error("Failed to search users: %s", e)
            raise
    
    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user statistics."""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return None
            
            # Get user's organizations count
            org_count = user.owned_organizations.count()
            
            # Get user's created namespaces count
            namespace_count = user.created_namespaces.count()
            
            return {
                'user_id': user_id,
                'organizations_count': org_count,
                'namespaces_count': namespace_count,
                'created_at': user.created_at,
                'verified': user.verified
            }
        except Exception as e:
            logger.error("Failed to get user stats: %s", e)
            raise