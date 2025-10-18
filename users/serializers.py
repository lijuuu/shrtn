"""
User serializers for data transformation with comprehensive validation.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - converts User object to/from JSON."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'username', 'verified', 
            'is_active', 'is_staff', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users with comprehensive validation."""
    
    # Custom field definitions with validation
    email = serializers.EmailField(
        required=True,
        max_length=254,
        help_text="Valid email address"
    )
    name = serializers.CharField(
        required=True,
        max_length=255,
        min_length=2,
        help_text="Full name (2-255 characters)"
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        min_length=3,
        help_text="Username (3-150 characters, alphanumeric and underscores only)"
    )
    password = serializers.CharField(
        required=True,
        min_length=8,
        max_length=128,
        write_only=True,
        help_text="Password (8-128 characters)"
    )
    
    class Meta:
        model = User
        fields = ['email', 'name', 'username', 'password']
    
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
    
    def validate_username(self, value):
        """Validate username format and uniqueness."""
        if not value:
            raise serializers.ValidationError("Username is required")
        
        # Check username format (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores"
            )
        
        # Check if username already exists
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists")
        
        return value.lower().strip()
    
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
    
    def validate(self, data):
        """Cross-field validation."""
        email = data.get('email', '')
        username = data.get('username', '')
        
        # Check if username is same as email prefix
        if email and username:
            email_prefix = email.split('@')[0]
            if username.lower() == email_prefix.lower():
                raise serializers.ValidationError({
                    'username': "Username cannot be the same as email prefix"
                })
        
        return data
    
    def create(self, validated_data):
        """Create a new user with hashed password."""
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating existing users with validation."""
    
    # Custom field definitions with validation
    email = serializers.EmailField(
        required=False,
        max_length=254,
        help_text="Valid email address"
    )
    name = serializers.CharField(
        required=False,
        max_length=255,
        min_length=2,
        help_text="Full name (2-255 characters)"
    )
    username = serializers.CharField(
        required=False,
        max_length=150,
        min_length=3,
        help_text="Username (3-150 characters, alphanumeric and underscores only)"
    )
    
    class Meta:
        model = User
        fields = ['email', 'name', 'username', 'verified', 'is_active']
    
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
    
    def validate_username(self, value):
        """Validate username format and uniqueness (excluding current user)."""
        if not value:
            return value
        
        # Check username format (alphanumeric and underscores only)
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores"
            )
        
        # Check if username already exists (excluding current user)
        current_user = self.instance
        if User.objects.filter(username=value).exclude(id=current_user.id).exists():
            raise serializers.ValidationError("A user with this username already exists")
        
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
    
    def validate(self, data):
        """Cross-field validation."""
        email = data.get('email', '')
        username = data.get('username', '')
        
        # Check if username is same as email prefix
        if email and username:
            email_prefix = email.split('@')[0]
            if username.lower() == email_prefix.lower():
                raise serializers.ValidationError({
                    'username': "Username cannot be the same as email prefix"
                })
        
        return data


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


class UserPasswordChangeSerializer(serializers.Serializer):
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
