"""
Enhanced serializers with permission context for frontend integration.
"""
from rest_framework import serializers
from .models import Organization, OrganizationMember, Invite
from core.dependencies.service_registry import service_registry

class OrganizationSerializer(serializers.ModelSerializer):
    """Basic organization serializer."""
    
    class Meta:
        model = Organization
        fields = [
            'org_id', 'name', 'description', 'created_at', 'updated_at'
        ]

class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Serializer for organization members."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'user_id', 'user_email', 'user_username', 
            'user_first_name', 'user_last_name',
            'can_view', 'can_update', 'can_admin',
            'joined_at'
        ]

class OrganizationWithPermissionsSerializer(serializers.ModelSerializer):
    """Enhanced organization serializer with user permissions."""
    
    # User's permissions in this organization
    user_permissions = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    namespace_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'org_id', 'name', 'description', 'created_at', 'updated_at',
            'user_permissions', 'user_role', 'member_count', 'namespace_count'
        ]
    
    def get_user_permissions(self, obj):
        """Get current user's permissions in this organization."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return {}
        
        try:
            organization_service = service_registry.get_organization_service()
            permissions = organization_service.get_user_permissions(obj.org_id, request.user.id)
            return permissions or {}
        except Exception:
            return {}
    
    def get_user_role(self, obj):
        """Get current user's role in this organization."""
        permissions = self.get_user_permissions(obj)
        
        if permissions.get('can_admin', False):
            return 'admin'
        elif permissions.get('can_update', False):
            return 'editor'
        elif permissions.get('can_view', False):
            return 'viewer'
        else:
            return 'none'
    
    def get_member_count(self, obj):
        """Get number of members in organization."""
        try:
            return OrganizationMember.objects.filter(organization_id=obj.org_id).count()
        except Exception:
            return 0
    
    def get_namespace_count(self, obj):
        """Get number of namespaces in organization."""
        try:
            from namespaces.models import Namespace
            return Namespace.objects.filter(organization_id=obj.org_id).count()
        except Exception:
            return 0

class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating organizations."""
    
    class Meta:
        model = Organization
        fields = ['name', 'description']
    
    def validate_name(self, value):
        """Validate organization name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Organization name must be at least 2 characters")
        return value.strip()

class OrganizationMemberCreateSerializer(serializers.Serializer):
    """Serializer for adding organization members."""
    
    user_id = serializers.UUIDField()
    can_view = serializers.BooleanField(default=True)
    can_update = serializers.BooleanField(default=False)
    can_admin = serializers.BooleanField(default=False)
    
    def validate_user_id(self, value):
        """Validate user exists."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

class InviteSerializer(serializers.ModelSerializer):
    """Serializer for organization invites."""
    
    inviter_email = serializers.CharField(source='inviter.email', read_only=True)
    inviter_username = serializers.CharField(source='inviter.username', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    expires_at_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Invite
        fields = [
            'invite_id', 'invitee_email', 'inviter_email', 'inviter_username',
            'organization_name', 'secret_token', 'used', 'expires_at',
            'expires_at_formatted', 'created_at'
        ]
    
    def get_expires_at_formatted(self, obj):
        """Get formatted expiration date."""
        if obj.expires_at:
            return obj.expires_at.strftime('%Y-%m-%d %H:%M:%S')
        return None

class InviteCreateSerializer(serializers.Serializer):
    """Serializer for creating organization invites."""
    
    invitee_email = serializers.EmailField()
    expires_in_hours = serializers.IntegerField(default=168, min_value=1, max_value=720)  # 1 hour to 30 days
    
    def validate_invitee_email(self, value):
        """Validate invitee email."""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email format")
        return value.lower().strip()

class OrganizationDetailSerializer(serializers.ModelSerializer):
    """Detailed organization serializer with full context."""
    
    user_permissions = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    members = OrganizationMemberSerializer(source='organizationmember_set', many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    namespace_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'org_id', 'name', 'description', 'created_at', 'updated_at',
            'user_permissions', 'user_role', 'members', 'member_count', 'namespace_count'
        ]
    
    def get_user_permissions(self, obj):
        """Get current user's permissions in this organization."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return {}
        
        try:
            organization_service = service_registry.get_organization_service()
            permissions = organization_service.get_user_permissions(obj.org_id, request.user.id)
            return permissions or {}
        except Exception:
            return {}
    
    def get_user_role(self, obj):
        """Get current user's role in this organization."""
        permissions = self.get_user_permissions(obj)
        
        if permissions.get('can_admin', False):
            return 'admin'
        elif permissions.get('can_update', False):
            return 'editor'
        elif permissions.get('can_view', False):
            return 'viewer'
        else:
            return 'none'
    
    def get_member_count(self, obj):
        """Get number of members in organization."""
        try:
            return OrganizationMember.objects.filter(organization_id=obj.org_id).count()
        except Exception:
            return 0
    
    def get_namespace_count(self, obj):
        """Get number of namespaces in organization."""
        try:
            from namespaces.models import Namespace
            return Namespace.objects.filter(organization_id=obj.org_id).count()
        except Exception:
            return 0