"""
User service for business logic.
"""
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

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with validation."""
        if not user_id or user_id <= 0:
            raise ValidationError("Invalid user ID")
        return self.repository.get_by_id(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email with validation."""
        if not email or '@' not in email:
            raise ValidationError("Invalid email format")
        return self.repository.get_by_email(email)

    def update(self, user_id: int, data: Dict[str, Any]) -> Optional[User]:
        """Update user with validation."""
        if not user_id or user_id <= 0:
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

    def delete(self, user_id: int) -> bool:
        """Delete user with validation."""
        if not user_id or user_id <= 0:
            raise ValidationError("Invalid user ID")
        return self.repository.delete(user_id)

    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[User]:
        """List users with optional filtering."""
        return self.repository.list(filters)

    def search_users(self, query: str) -> List[User]:
        """Search users by name."""
        if not query or len(query.strip()) < 2:
            raise ValidationError("Search query must be at least 2 characters")
        return self.repository.search_by_name(query.strip())

    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user statistics."""
        if not user_id or user_id <= 0:
            raise ValidationError("Invalid user ID")
        return self.repository.get_user_stats(user_id)