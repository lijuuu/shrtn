"""
Base serializers with common functionality.
"""
from rest_framework import serializers
from typing import Any, Dict, Optional
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer with common functionality.
    """
    
    def to_representation(self, instance):
        """Override to add common fields."""
        data = super().to_representation(instance)
        
        # Add common metadata if needed
        if hasattr(instance, 'created_at'):
            data['created_at'] = instance.created_at.isoformat() if instance.created_at else None
        
        return data


class BaseCreateSerializer(BaseModelSerializer):
    """
    Base serializer for create operations.
    """
    
    def create(self, validated_data):
        """Override create to add common fields."""
        # Add created_by if not present and user is available
        if 'created_by' not in validated_data and hasattr(self.context.get('request'), 'user'):
            validated_data['created_by'] = self.context['request'].user
        
        return super().create(validated_data)


class BaseUpdateSerializer(BaseModelSerializer):
    """
    Base serializer for update operations.
    """
    
    def update(self, instance, validated_data):
        """Override update to add common fields."""
        # Add updated_by if not present and user is available
        if 'updated_by' not in validated_data and hasattr(self.context.get('request'), 'user'):
            validated_data['updated_by'] = self.context['request'].user
        
        return super().update(instance, validated_data)


class UserContextMixin:
    """
    Mixin to add user context to serializers.
    """
    
    def get_user_permissions(self, obj) -> Optional[Dict[str, bool]]:
        """Get user permissions for the object."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # This should be implemented by subclasses
        return None


class PermissionSerializerMixin(UserContextMixin):
    """
    Mixin to add permission fields to serializers.
    """
    
    user_permissions = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    def get_user_permissions(self, obj) -> Dict[str, bool]:
        """Get user permissions for the object."""
        permissions = super().get_user_permissions(obj)
        if permissions:
            return {
                'can_view': permissions.get('can_view', False),
                'can_update': permissions.get('can_update', False),
                'can_admin': permissions.get('can_admin', False)
            }
        return {
            'can_view': False,
            'can_update': False,
            'can_admin': False
        }
    
    def get_user_role(self, obj) -> str:
        """Get user role for the object."""
        permissions = super().get_user_permissions(obj)
        if permissions:
            return permissions.get('role', 'none')
        return 'none'
