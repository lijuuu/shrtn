"""
Namespace serializers for data transformation.
"""
from rest_framework import serializers
from .models import Namespace


class NamespaceSerializer(serializers.ModelSerializer):
    """Serializer for Namespace model."""
    
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    creator_name = serializers.CharField(source='created_by.name', read_only=True)
    
    class Meta:
        model = Namespace
        fields = [
            'namespace_id', 'organization', 'organization_name', 'created_by',
            'creator_name', 'name', 'created_at'
        ]
        read_only_fields = ['namespace_id', 'created_at']


class NamespaceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating namespaces."""
    
    class Meta:
        model = Namespace
        fields = ['name']
    
    def validate_name(self, value):
        """Validate namespace name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Namespace name must be at least 2 characters")
        
        # Check format (alphanumeric, hyphens, underscores only)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', value.strip()):
            raise serializers.ValidationError(
                "Namespace name can only contain letters, numbers, hyphens, and underscores"
            )
        
        return value.strip().lower()


class NamespaceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating namespaces."""
    
    class Meta:
        model = Namespace
        fields = ['name']
    
    def validate_name(self, value):
        """Validate namespace name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Namespace name must be at least 2 characters")
        
        # Check format (alphanumeric, hyphens, underscores only)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', value.strip()):
            raise serializers.ValidationError(
                "Namespace name can only contain letters, numbers, hyphens, and underscores"
            )
        
        return value.strip().lower()


class NamespaceAvailabilitySerializer(serializers.Serializer):
    """Serializer for namespace availability check."""
    
    name = serializers.CharField(max_length=255)
    available = serializers.BooleanField(read_only=True)
    
    def validate_name(self, value):
        """Validate namespace name format."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Namespace name must be at least 2 characters")
        
        # Check format (alphanumeric, hyphens, underscores only)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', value.strip()):
            raise serializers.ValidationError(
                "Namespace name can only contain letters, numbers, hyphens, and underscores"
            )
        
        return value.strip().lower()
