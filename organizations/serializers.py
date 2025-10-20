"""
Enhanced serializers with permission context for frontend integration.
"""
from rest_framework import serializers
from .models import Organization, OrganizationMember, Invite
from core.dependencies.service_registry import service_registry
from core.serializers.base import BaseModelSerializer, BaseCreateSerializer, BaseUpdateSerializer, PermissionSerializerMixin

class OrganizationSerializer(BaseModelSerializer):
    """Basic organization serializer."""
    
    class Meta:
        model = Organization
        fields = [
            'org_id', 'name', 'created_at', 'updated_at'
        ]

class OrganizationMemberSerializer(BaseModelSerializer):
    """Serializer for organization members."""
    
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'user_id', 'user_name', 'user_email', 'role', 'joined_at'
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
            'org_id', 'name', 'created_at', 'updated_at',
            'user_permissions', 'user_role', 'member_count', 'namespace_count'
        ]
    
    def get_user_permissions(self, obj):
        """Get current user's permissions in this organization."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return {}
        
        try:
            organization_service = service_registry.get_organization_service()
            member = organization_service.get_member_by_user(obj.org_id, request.user.id)
            if member:
                return {
                    'role': member.role
                }
            return {}
        except Exception:
            return {}
    
    def get_user_role(self, obj):
        """Get current user's role in this organization."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return 'none'
        
        try:
            organization_service = service_registry.get_organization_service()
            member = organization_service.get_member_by_user(obj.org_id, request.user.id)
            return member.role if member else 'none'
        except Exception:
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

class OrganizationCreateSerializer(serializers.Serializer):
    """Serializer for creating organizations."""
    
    name = serializers.CharField(max_length=255)
    owner = serializers.UUIDField()
    
    def validate_name(self, value):
        """Validate organization name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Organization name must be at least 2 characters")
        return value.strip()
    
    def validate_owner(self, value):
        """Validate owner ID."""
        if not value:
            raise serializers.ValidationError("Owner is required")
        return value

class OrganizationMemberCreateSerializer(serializers.Serializer):
    """Serializer for adding organization members."""
    
    user_id = serializers.UUIDField()
    role = serializers.ChoiceField(choices=OrganizationMember.ROLE_CHOICES, default='viewer')
    
    def validate_user_id(self, value):
        """Validate user exists."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            User.objects.get(id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

class OrganizationMemberUpdateSerializer(serializers.Serializer):
    """Serializer for updating member roles."""
    
    role = serializers.ChoiceField(choices=OrganizationMember.ROLE_CHOICES)

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
            'organization_name', 'role', 'secret', 'used', 'expires_at',
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
    role = serializers.ChoiceField(choices=OrganizationMember.ROLE_CHOICES, default='viewer')
    expires_in_hours = serializers.IntegerField(default=168, min_value=1, max_value=720)  # 1 hour to 30 days
    org_id = serializers.UUIDField(required=False)  # Will be set by the view
    inviter_user_id = serializers.UUIDField(required=False)  # Will be set by the view
    
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
            'org_id', 'name', 'created_at', 'updated_at',
            'user_permissions', 'user_role', 'members', 'member_count', 'namespace_count'
        ]
    
    def get_user_permissions(self, obj):
        """Get current user's permissions in this organization."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return {}
        
        try:
            organization_service = service_registry.get_organization_service()
            member = organization_service.get_member_by_user(obj.org_id, request.user.id)
            if member:
                return {
                    'role': member.role
                }
            return {}
        except Exception:
            return {}
    
    def get_user_role(self, obj):
        """Get current user's role in this organization."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return 'none'
        
        try:
            organization_service = service_registry.get_organization_service()
            member = organization_service.get_member_by_user(obj.org_id, request.user.id)
            return member.role if member else 'none'
        except Exception:
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