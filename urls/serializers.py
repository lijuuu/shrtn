"""
URL serializers for data transformation.
"""
from rest_framework import serializers
from .models import ShortUrl, BulkMapping


class ShortUrlSerializer(serializers.Serializer):
    """Serializer for ShortUrl model."""
    
    namespace_id = serializers.IntegerField()
    shortcode = serializers.CharField(max_length=255)
    created_by_user_id = serializers.IntegerField()
    original_url = serializers.URLField()
    expiry = serializers.DateTimeField(required=False, allow_null=True)
    click_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    is_private = serializers.BooleanField(default=False)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )


class ShortUrlCreateSerializer(serializers.Serializer):
    """Serializer for creating short URLs."""
    
    shortcode = serializers.CharField(max_length=255, required=False, allow_blank=True)
    original_url = serializers.URLField()
    expiry = serializers.DateTimeField(required=False, allow_null=True)
    is_private = serializers.BooleanField(default=False)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )
    
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
            raise serializers.ValidationError("Enter a valid URL")
        
        return value
    
    def validate_shortcode(self, value):
        """Validate shortcode format."""
        if value:
            # Check format (alphanumeric, hyphens, underscores only)
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', value):
                raise serializers.ValidationError(
                    "Shortcode can only contain letters, numbers, hyphens, and underscores"
                )
            
            if len(value) < 3:
                raise serializers.ValidationError("Shortcode must be at least 3 characters")
        
        return value


class ShortUrlUpdateSerializer(serializers.Serializer):
    """Serializer for updating short URLs."""
    
    original_url = serializers.URLField(required=False)
    expiry = serializers.DateTimeField(required=False, allow_null=True)
    is_private = serializers.BooleanField(required=False)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )
    
    def validate_original_url(self, value):
        """Validate original URL."""
        if value:
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
                raise serializers.ValidationError("Enter a valid URL")
        
        return value


class BulkMappingSerializer(serializers.Serializer):
    """Serializer for bulk URL mapping."""
    
    shortcode = serializers.CharField(max_length=255)
    original_url = serializers.URLField()
    
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
            raise serializers.ValidationError("Enter a valid URL")
        
        return value
    
    def validate_shortcode(self, value):
        """Validate shortcode format."""
        if not value:
            raise serializers.ValidationError("Shortcode is required")
        
        # Check format (alphanumeric, hyphens, underscores only)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise serializers.ValidationError(
                "Shortcode can only contain letters, numbers, hyphens, and underscores"
            )
        
        if len(value) < 3:
            raise serializers.ValidationError("Shortcode must be at least 3 characters")
        
        return value


class BulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk URL creation."""
    
    urls = serializers.ListField(
        child=BulkMappingSerializer(),
        min_length=1,
        max_length=1000  # Limit bulk operations
    )
    
    def validate_urls(self, value):
        """Validate bulk URLs."""
        if not value:
            raise serializers.ValidationError("At least one URL is required")
        
        # Check for duplicate shortcodes
        shortcodes = [url['shortcode'] for url in value]
        if len(shortcodes) != len(set(shortcodes)):
            raise serializers.ValidationError("Duplicate shortcodes are not allowed")
        
        return value
