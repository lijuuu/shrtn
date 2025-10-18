"""
Organization repository for PostgreSQL operations.
"""
import uuid
import logging
from typing import List, Optional, Dict, Any
from core.database.base import Repository
from core.database.postgres import PostgreSQLConnection
from .models import Organization, OrganizationMember, Invite

logger = logging.getLogger(__name__)


class OrganizationRepository(Repository):
    """Repository for Organization operations using PostgreSQL."""
    
    def __init__(self, connection: PostgreSQLConnection):
        super().__init__(connection)
        self.postgres = connection
    
    def create(self, data: Dict[str, Any]) -> Organization:
        """Create a new organization."""
        try:
            organization = Organization.objects.create(
                name=data['name'],
                owner_id=data['owner_id']
            )
            logger.info("Created organization: %s", organization.name)
            return organization
        except Exception as e:
            logger.error("Failed to create organization: %s", e)
            raise
    
    def get_by_id(self, org_id: uuid.UUID) -> Optional[Organization]:
        """Get organization by ID."""
        try:
            return Organization.objects.get(org_id=org_id)
        except Organization.DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get organization by ID: %s", e)
            raise
    
    def update(self, org_id: uuid.UUID, data: Dict[str, Any]) -> Optional[Organization]:
        """Update organization."""
        try:
            organization = self.get_by_id(org_id)
            if not organization:
                return None
            
            for field, value in data.items():
                if hasattr(organization, field):
                    setattr(organization, field, value)
            
            organization.save()
            logger.info("Updated organization: %s", organization.name)
            return organization
        except Exception as e:
            logger.error("Failed to update organization: %s", e)
            raise
    
    def delete(self, org_id: uuid.UUID) -> bool:
        """Delete organization."""
        try:
            organization = self.get_by_id(org_id)
            if not organization:
                return False
            
            organization.delete()
            logger.info("Deleted organization: %s", organization.name)
            return True
        except Exception as e:
            logger.error("Failed to delete organization: %s", e)
            raise
    
    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Organization]:
        """List organizations with optional filters."""
        try:
            queryset = Organization.objects.all()
            
            if filters:
                if 'owner_id' in filters:
                    queryset = queryset.filter(owner_id=filters['owner_id'])
                if 'user_id' in filters:
                    # Get organizations where user is a member
                    queryset = queryset.filter(
                        members__user_id=filters['user_id']
                    ).distinct()
            
            return list(queryset)
        except Exception as e:
            logger.error("Failed to list organizations: %s", e)
            raise
    
    def add_member(self, org_id: uuid.UUID, user_id: uuid.UUID, permissions: Dict[str, bool]) -> OrganizationMember:
        """Add member to organization."""
        try:
            member = OrganizationMember.objects.create(
                organization_id=org_id,
                user_id=user_id,
                can_view=permissions.get('can_view', False),
                can_admin=permissions.get('can_admin', False),
                can_update=permissions.get('can_update', False)
            )
            logger.info("Added member %s to organization %s", user_id, org_id)
            return member
        except Exception as e:
            logger.error("Failed to add member: %s", e)
            raise
    
    def remove_member(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Remove member from organization."""
        try:
            member = OrganizationMember.objects.get(
                organization_id=org_id,
                user_id=user_id
            )
            member.delete()
            logger.info("Removed member %s from organization %s", user_id, org_id)
            return True
        except OrganizationMember.DoesNotExist:
            return False
        except Exception as e:
            logger.error("Failed to remove member: %s", e)
            raise
    
    def get_members(self, org_id: uuid.UUID) -> List[OrganizationMember]:
        """Get organization members."""
        try:
            return list(OrganizationMember.objects.filter(organization_id=org_id))
        except Exception as e:
            logger.error("Failed to get members: %s", e)
            raise
    
    def get_user_permissions(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Dict[str, bool]]:
        """Get user permissions in organization."""
        try:
            member = OrganizationMember.objects.get(
                organization_id=org_id,
                user_id=user_id
            )
            return {
                'can_view': member.can_view,
                'can_admin': member.can_admin,
                'can_update': member.can_update
            }
        except OrganizationMember.DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get user permissions: %s", e)
            raise
    
    def create_invite(self, data: Dict[str, Any]) -> Invite:
        """Create organization invite."""
        try:
            invite = Invite.objects.create(
                invitee_email=data['invitee_email'],
                organization_id=data['org_id'],
                inviter_user_id=data['inviter_user_id'],
                can_view=data.get('can_view', False),
                can_admin=data.get('can_admin', False),
                can_update=data.get('can_update', False),
                secret=data['secret'],
                expires_at=data['expires_at']
            )
            logger.info("Created invite for %s to organization %s", data['invitee_email'], data['org_id'])
            return invite
        except Exception as e:
            logger.error("Failed to create invite: %s", e)
            raise
    
    def get_invite_by_secret(self, secret: str) -> Optional[Invite]:
        """Get invite by secret token."""
        try:
            return Invite.objects.get(secret=secret)
        except Invite.DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get invite by secret: %s", e)
            raise
    
    def get_pending_invites(self, org_id: uuid.UUID) -> List[Invite]:
        """Get pending invites for organization."""
        try:
            return list(Invite.objects.filter(
                organization_id=org_id,
                used=False
            ))
        except Exception as e:
            logger.error("Failed to get pending invites: %s", e)
            raise
    
    def get_invite_by_id(self, invite_id: uuid.UUID) -> Optional[Invite]:
        """Get invite by ID."""
        try:
            return Invite.objects.get(invite_id=invite_id)
        except Invite.DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get invite by ID: %s", e)
            raise
    
    def mark_invite_unused(self, invite_id: uuid.UUID) -> bool:
        """Mark invite as unused (rollback)."""
        try:
            invite = self.get_invite_by_id(invite_id)
            if not invite:
                return False
            
            invite.used = False
            invite.save()
            return True
        except Exception as e:
            logger.error("Failed to mark invite as unused: %s", e)
            raise
    
    def mark_invite_used(self, invite_id: uuid.UUID) -> bool:
        """Mark invite as used."""
        try:
            invite = Invite.objects.get(invite_id=invite_id)
            invite.used = True
            invite.save()
            logger.info("Marked invite %s as used", invite_id)
            return True
        except Invite.DoesNotExist:
            return False
        except Exception as e:
            logger.error("Failed to mark invite as used: %s", e)
            raise
