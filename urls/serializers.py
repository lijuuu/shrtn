"""
Enhanced URL serializers with permission context for frontend integration.
"""
from rest_framework import serializers
from .models import ShortUrl
from core.dependencies.service_registry import service_registry
from datetime import datetime

class ShortUrlSerializer(serializers.ModelSerializer):
    """Basic short URL serializer."""
    
    class Meta:
        model = ShortUrl
        fields = [
            'namespace_id', 'shortcode', 'original_url', 'title', 'description',
            'created_by_user_id', 'created_at', 'updated_at', 'expires_at',
            'click_count', 'is_active'
        ]

class ShortUrlWithPermissionsSerializer(serializers.ModelSerializer):
    """Enhanced short URL serializer with user permissions."""
    
    # User's permissions in this URL's namespace organization
    user_permissions = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    namespace_name = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    short_url = serializers.SerializerMethodField()
    expires_at_formatted = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ShortUrl
        fields = [
            'namespace_id', 'shortcode', 'original_url', 'title', 'description',
            'created_by_user_id', 'created_at', 'created_at_formatted', 'updated_at', 
            'expires_at', 'expires_at_formatted', 'click_count', 'is_active',
            'user_permissions', 'user_role', 'namespace_name', 'organization_name',
            'short_url'
        ]
    
    def get_user_permissions(self, obj):
        """Get current user's permissions in this URL's namespace organization."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return {}
        
        try:
            # Get namespace to find organization
            namespace_service = service_registry.get_namespace_service()
            namespace = namespace_service.get_by_id(obj.namespace_id)
            if not namespace:
                return {}
            
            organization_service = service_registry.get_organization_service()
            permissions = organization_service.get_user_permissions(namespace.organization_id, request.user.id)
            return permissions or {}
        except Exception:
            return {}
    
    def get_user_role(self, obj):
        """Get current user's role in this URL's namespace organization."""
        permissions = self.get_user_permissions(obj)
        
        if permissions.get('can_admin', False):
            return 'admin'
        elif permissions.get('can_update', False):
            return 'editor'
        elif permissions.get('can_view', False):
            return 'viewer'
        else:
            return 'none'
    
    def get_namespace_name(self, obj):
        """Get namespace name."""
        try:
            namespace_service = service_registry.get_namespace_service()
            namespace = namespace_service.get_by_id(obj.namespace_id)
            return namespace.name if namespace else None
        except Exception:
            return None
    
    def get_organization_name(self, obj):
        """Get organization name."""
        try:
            namespace_service = service_registry.get_namespace_service()
            namespace = namespace_service.get_by_id(obj.namespace_id)
            if namespace:
                return namespace.organization.name
            return None
        except Exception:
            return None
    
    def get_short_url(self, obj):
        """Get the full short URL."""
        try:
            namespace_service = service_registry.get_namespace_service()
            namespace = namespace_service.get_by_id(obj.namespace_id)
            if namespace:
                request = self.context.get('request')
                base_url = request.build_absolute_uri('/') if request else 'http://localhost:8000/'
                return f"{base_url.rstrip('/')}/{namespace.name}/{obj.shortcode}/"
            return None
        except Exception:
            return None
    
    def get_expires_at_formatted(self, obj):
        """Get formatted expiration date."""
        if obj.expires_at:
            return obj.expires_at.strftime('%Y-%m-%d %H:%M:%S')
        return None
    
    def get_created_at_formatted(self, obj):
        """Get formatted creation date."""
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return None

class ShortUrlCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating short URLs."""
    
    class Meta:
        model = ShortUrl
        fields = [
            'original_url', 'title', 'description', 'shortcode', 'expires_at'
        ]
    
    def validate_original_url(self, value):
        """Validate original URL."""
        if not value:
            raise serializers.ValidationError("Original URL is required")
        
        # Basic URL validation
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(value):
            raise serializers.ValidationError("Invalid URL format")
        
        return value
    
    def validate_shortcode(self, value):
        """Validate shortcode if provided."""
        if value:
            # Check for invalid characters
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', value):
                raise serializers.ValidationError("Shortcode can only contain letters, numbers, hyphens, and underscores")
            
            if len(value) < 3:
                raise serializers.ValidationError("Shortcode must be at least 3 characters")
        
        return value

class ShortUrlUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating short URLs."""
    
    class Meta:
        model = ShortUrl
        fields = ['original_url', 'title', 'description', 'expires_at', 'is_active']
    
    def validate_original_url(self, value):
        """Validate original URL."""
        if not value:
            raise serializers.ValidationError("Original URL is required")
        
        # Basic URL validation
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(value):
            raise serializers.ValidationError("Invalid URL format")
        
        return value

class BulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk URL creation."""
    
    urls = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        min_length=1,
        max_length=1000
    )
    method = serializers.ChoiceField(
        choices=['random', 'custom'],
        default='random'
    )
    
    def validate_urls(self, value):
        """Validate URLs list."""
        if not value:
            raise serializers.ValidationError("URLs list cannot be empty")
        
        # Validate each URL entry
        for i, url_data in enumerate(value):
            if 'url' not in url_data:
                raise serializers.ValidationError(f"URL entry {i+1} must have 'url' field")
            
            # Basic URL validation
            import re
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(url_data['url']):
                raise serializers.ValidationError(f"Invalid URL format in entry {i+1}")
        
        return value

class URLStatsSerializer(serializers.Serializer):
    """Serializer for URL statistics."""
    
    total_urls = serializers.IntegerField()
    active_urls = serializers.IntegerField()
    expired_urls = serializers.IntegerField()
    total_clicks = serializers.IntegerField()
    top_urls = serializers.ListField(
        child=serializers.DictField()
    )