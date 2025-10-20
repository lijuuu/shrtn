"""
Enhanced namespace serializers with permission context for frontend integration.
"""
from rest_framework import serializers
from .models import Namespace
from core.dependencies.service_registry import service_registry
from core.serializers.base import BaseModelSerializer, BaseCreateSerializer, BaseUpdateSerializer, PermissionSerializerMixin

class NamespaceSerializer(BaseModelSerializer):
    """Basic namespace serializer."""
    
    class Meta:
        model = Namespace
        fields = [
            'namespace_id', 'name', 'organization', 'created_by', 'created_at'
        ]

class NamespaceWithPermissionsSerializer(PermissionSerializerMixin, BaseModelSerializer):
    """Enhanced namespace serializer with user permissions."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    creator_username = serializers.CharField(source='created_by.username', read_only=True)
    url_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Namespace
        fields = [
            'namespace_id', 'name', 'description', 'organization_id', 'organization_name',
            'created_by_id', 'creator_username', 'created_at', 'updated_at',
            'user_permissions', 'user_role', 'url_count'
        ]
    
    def get_user_permissions(self, obj):
        """Get current user's permissions in this namespace's organization."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return {}
        
        try:
            organization_service = service_registry.get_organization_service()
            permissions = organization_service.get_user_permissions(obj.organization_id, request.user.id)
            return permissions or {}
        except Exception:
            return {}
    
    def get_user_role(self, obj):
        """Get current user's role in this namespace's organization."""
        permissions = self.get_user_permissions(obj)
        
        if permissions.get('can_admin', False):
            return 'admin'
        elif permissions.get('can_update', False):
            return 'editor'
        elif permissions.get('can_view', False):
            return 'viewer'
        else:
            return 'none'
    
    def get_url_count(self, obj):
        """Get number of URLs in this namespace."""
        try:
            url_service = service_registry.get_url_service()
            urls = url_service.get_by_namespace(obj.namespace_id)
            return len(urls) if urls else 0
        except Exception:
            return 0

class NamespaceCreateSerializer(BaseCreateSerializer):
    """Serializer for creating namespaces."""
    
    class Meta:
        model = Namespace
        fields = ['name']
    
    def validate_name(self, value):
        """Validate namespace name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Namespace name must be at least 2 characters")
        
        # Check global uniqueness
        try:
            namespace_service = service_registry.get_namespace_service()
            if not namespace_service.check_name_availability(value.strip().lower()):
                raise serializers.ValidationError("Namespace name is already taken")
        except Exception:
            pass  # Skip validation if service not available
        
        return value.strip().lower()

class NamespaceUpdateSerializer(BaseUpdateSerializer):
    """Serializer for updating namespaces."""
    
    class Meta:
        model = Namespace
        fields = ['name']
    
    def validate_name(self, value):
        """Validate namespace name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Namespace name must be at least 2 characters")
        
        # Check global uniqueness (excluding current namespace)
        try:
            namespace_service = service_registry.get_namespace_service()
            existing = namespace_service.get_by_name(value.strip().lower())
            if existing and existing.namespace_id != self.instance.namespace_id:
                raise serializers.ValidationError("Namespace name is already taken")
        except Exception:
            pass  # Skip validation if service not available
        
        return value.strip().lower()

class NamespaceAvailabilitySerializer(serializers.Serializer):
    """Serializer for namespace availability check."""
    
    name = serializers.CharField(max_length=100)
    available = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True)
    
    def validate_name(self, value):
        """Validate namespace name format."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Namespace name must be at least 2 characters")
        
        # Check for invalid characters
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', value.strip()):
            raise serializers.ValidationError("Namespace name can only contain letters, numbers, hyphens, and underscores")
        
        return value.strip().lower()