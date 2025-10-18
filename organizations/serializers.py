"""
Organization serializers for data transformation.
"""
from rest_framework import serializers
from .models import Organization, OrganizationMember, Invite


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""
    
    class Meta:
        model = Organization
        fields = [
            'org_id', 'name', 'owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['org_id', 'created_at', 'updated_at']


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating organizations."""
    
    class Meta:
        model = Organization
        fields = ['name']
    
    def validate_name(self, value):
        """Validate organization name."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Organization name must be at least 2 characters")
        return value.strip()


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Serializer for Organization Member model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'user', 'user_email', 'user_name', 'can_view', 'can_admin', 
            'can_update', 'joined_at'
        ]
        read_only_fields = ['joined_at']


class OrganizationMemberCreateSerializer(serializers.ModelSerializer):
    """Serializer for adding organization members."""
    
    class Meta:
        model = OrganizationMember
        fields = ['user', 'can_view', 'can_admin', 'can_update']


class InviteSerializer(serializers.ModelSerializer):
    """Serializer for Invite model."""
    
    inviter_name = serializers.CharField(source='inviter.name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Invite
        fields = [
            'invite_id', 'invitee_email', 'organization', 'organization_name',
            'inviter', 'inviter_name', 'can_view', 'can_admin', 'can_update',
            'used', 'created_at', 'expires_at'
        ]
        read_only_fields = ['invite_id', 'used', 'created_at']


class InviteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invites."""
    
    class Meta:
        model = Invite
        fields = ['invitee_email', 'can_view', 'can_admin', 'can_update']
    
    def validate_invitee_email(self, value):
        """Validate invitee email."""
        if not value or '@' not in value:
            raise serializers.ValidationError("Enter a valid email address")
        return value.lower().strip()
