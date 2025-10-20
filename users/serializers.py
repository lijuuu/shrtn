"""
User serializers for data transformation with comprehensive validation.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """Public user serializer - limited fields for public display."""
    
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'verified']
        read_only_fields = ['id']


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user list views - optimized for listing."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'username', 'verified', 'created_at']
        read_only_fields = ['id', 'created_at']


# Authentication serializers moved from authentication app
class UserRegistrationSerializer(serializers.Serializer):
    """Serializer for user registration with comprehensive validation."""
    
    email = serializers.EmailField(
        required=True,
        max_length=254,
        help_text="Valid email address"
    )
    password = serializers.CharField(
        required=True,
        min_length=8,
        max_length=128,
        write_only=True,
        help_text="Password (8-128 characters)"
    )
    name = serializers.CharField(
        required=True,
        max_length=255,
        min_length=2,
        help_text="Full name (2-255 characters)"
    )
    organization_name = serializers.CharField(
        required=False,
        max_length=255,
        allow_blank=True,
        help_text="Organization name (optional)"
    )
    
    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if not value:
            raise serializers.ValidationError("Email is required")
        
        # Check email format
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address")
        
        # Check if email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        
        return value.lower().strip()
    
    def validate_password(self, value):
        """Validate password strength."""
        if not value:
            raise serializers.ValidationError("Password is required")
        
        # Check minimum length
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        # Check for at least one digit
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character")
        
        return value
    
    def validate_name(self, value):
        """Validate name format."""
        if not value:
            raise serializers.ValidationError("Name is required")
        
        # Check if name contains only letters, spaces, and common punctuation
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError(
                "Name can only contain letters, spaces, hyphens, apostrophes, and periods"
            )
        
        return value.strip()


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField(
        required=True,
        help_text="User email address"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="User password"
    )
    
    def validate_email(self, value):
        """Validate email format."""
        if not value:
            raise serializers.ValidationError("Email is required")
        
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address")
        
        return value.lower().strip()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'username', 'verified', 
            'is_active', 'google_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    name = serializers.CharField(
        required=False,
        max_length=255,
        min_length=2,
        help_text="Full name (2-255 characters)"
    )
    email = serializers.EmailField(
        required=False,
        max_length=254,
        help_text="Valid email address"
    )
    
    class Meta:
        model = User
        fields = ['name', 'email']
    
    def validate_email(self, value):
        """Validate email format and uniqueness (excluding current user)."""
        if not value:
            return value
        
        # Check email format
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address")
        
        # Check if email already exists (excluding current user)
        current_user = self.instance
        if User.objects.filter(email=value).exclude(id=current_user.id).exists():
            raise serializers.ValidationError("A user with this email already exists")
        
        return value.lower().strip()
    
    def validate_name(self, value):
        """Validate name format."""
        if not value:
            return value
        
        # Check if name contains only letters, spaces, and common punctuation
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise serializers.ValidationError(
                "Name can only contain letters, spaces, hyphens, apostrophes, and periods"
            )
        
        return value.strip()


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Current password"
    )
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        max_length=128,
        write_only=True,
        help_text="New password (8-128 characters)"
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Confirm new password"
    )
    
    def validate_current_password(self, value):
        """Validate current password."""
        if not value:
            raise serializers.ValidationError("Current password is required")
        return value
    
    def validate_new_password(self, value):
        """Validate new password strength."""
        if not value:
            raise serializers.ValidationError("New password is required")
        
        # Check minimum length
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        # Check for at least one digit
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character")
        
        return value
    
    def validate(self, data):
        """Cross-field validation."""
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        # Check if new password and confirm password match
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': "New password and confirm password do not match"
            })
        
        # Check if new password is different from current password
        current_password = data.get('current_password')
        if current_password and new_password == current_password:
            raise serializers.ValidationError({
                'new_password': "New password must be different from current password"
            })
        
        return data


class AuthResponseSerializer(serializers.Serializer):
    """Serializer for authentication response data."""
    
    user = UserProfileSerializer()
    tokens = serializers.DictField()
    organization = serializers.DictField(required=False)


class AuthStatusSerializer(serializers.Serializer):
    """Serializer for authentication status response."""
    
    authenticated = serializers.BooleanField()
    user = UserProfileSerializer(required=False, allow_null=True)
    tokens = serializers.DictField(required=False, allow_null=True)


class GoogleLoginSerializer(serializers.Serializer):
    """Serializer for Google OAuth login."""
    
    google_id = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Google user ID"
    )
    email = serializers.EmailField(
        required=True,
        help_text="Google account email"
    )
    name = serializers.CharField(
        required=True,
        max_length=255,
        help_text="Full name from Google"
    )
    picture = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Profile picture URL from Google"
    )
    
    def validate_google_id(self, value):
        """Validate Google ID format."""
        if not value:
            raise serializers.ValidationError("Google ID is required")
        
        # Google IDs are typically numeric strings
        if not value.isdigit():
            raise serializers.ValidationError("Invalid Google ID format")
        
        return value
    
    def validate_email(self, value):
        """Validate email format."""
        if not value:
            raise serializers.ValidationError("Email is required")
        
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address")
        
        return value.lower().strip()
    
    def validate_name(self, value):
        """Validate name format."""
        if not value:
            raise serializers.ValidationError("Name is required")
        
        return value.strip()


