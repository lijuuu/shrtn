"""
Custom JWT authentication with claims.
"""
import logging
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from typing import Dict, Any, Optional
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

logger = logging.getLogger(__name__)
User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """Custom JWT authentication with user claims."""
    
    def authenticate(self, request: Request):
        """Authenticate user using JWT token."""
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = self.decode_token(token)
            user_id = payload.get('user_id')
            
            if not user_id:
                raise AuthenticationFailed('Invalid token: missing user_id')
            
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise AuthenticationFailed('User not found')
            
            # Add custom claims to user object
            user.jwt_claims = payload
            
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            logger.error("JWT authentication error: %s", e)
            raise AuthenticationFailed('Authentication failed')
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token."""
        secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
        algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
        
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    
    @staticmethod
    def generate_token(user, additional_claims: Dict[str, Any] = None) -> str:
        """Generate JWT token for user with custom claims."""
        secret_key = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
        algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
        expiration_hours = getattr(settings, 'JWT_EXPIRATION_HOURS', 24)
        
        payload = {
            'user_id': user.id,
            'email': user.email,
            'username': user.username,
            'name': user.get_full_name(),
            'verified': user.verified,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
        }
        
        # Add organization information
        try:
            organizations = JWTAuthentication.get_user_organizations(user)
            payload['organizations'] = [
                {
                    'id': org.org_id,
                    'name': org.name,
                    'role': 'admin'  # User is admin of their own organizations
                } for org in organizations
            ]
        except Exception as e:
            logger.warning("Failed to load user organizations for JWT: %s", e)
            payload['organizations'] = []
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, secret_key, algorithm=algorithm)
    
    @staticmethod
    def get_user_organizations(user) -> list:
        """Get user's organizations with roles."""
        try:
            from core.dependencies.service_registry import service_registry
            org_service = service_registry.get_organization_service()
            return org_service.get_user_organizations(user.id)
        except Exception as e:
            logger.error("Failed to get user organizations: %s", e)
            return []
    
    @staticmethod
    def get_user_permissions(user, organization_id: int) -> Dict[str, bool]:
        """Get user permissions for a specific organization."""
        try:
            from core.dependencies.service_registry import service_registry
            org_service = service_registry.get_organization_service()
            return org_service.get_user_permissions(organization_id, user.id) or {}
        except Exception as e:
            logger.error("Failed to get user permissions: %s", e)
            return {}


class PermissionMixin:
    """Mixin for permission checking."""
    
    def has_permission(self, user, organization_id: int, permission: str) -> bool:
        """Check if user has specific permission in organization."""
        permissions = JWTAuthentication.get_user_permissions(user, organization_id)
        return permissions.get(permission, False)
    
    def is_admin(self, user, organization_id: int) -> bool:
        """Check if user is admin in organization."""
        return self.has_permission(user, organization_id, 'can_admin')
    
    def is_editor(self, user, organization_id: int) -> bool:
        """Check if user is editor in organization."""
        return self.has_permission(user, organization_id, 'can_update')
    
    def is_viewer(self, user, organization_id: int) -> bool:
        """Check if user is viewer in organization."""
        return self.has_permission(user, organization_id, 'can_view')
    
    def can_create_namespace(self, user, organization_id: int) -> bool:
        """Check if user can create namespace."""
        return self.is_admin(user, organization_id)
    
    def can_invite_users(self, user, organization_id: int) -> bool:
        """Check if user can invite users."""
        return self.is_admin(user, organization_id)
    
    def can_manage_urls(self, user, organization_id: int) -> bool:
        """Check if user can manage URLs (create/edit/delete)."""
        return self.is_admin(user, organization_id) or self.is_editor(user, organization_id)
    
    def can_view_urls(self, user, organization_id: int) -> bool:
        """Check if user can view URLs."""
        return (self.is_admin(user, organization_id) or 
                self.is_editor(user, organization_id) or 
                self.is_viewer(user, organization_id))
