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
    
    def add_member(self, org_id: uuid.UUID, user_id: uuid.UUID, role: str = 'viewer') -> OrganizationMember:
        """Add member to organization with role."""
        try:
            member = OrganizationMember.objects.create(
                organization_id=org_id,
                user_id=user_id,
                role=role
            )
            logger.info("Added member %s to organization %s with role %s", user_id, org_id, role)
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
    
    def get_member_by_user(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Optional[OrganizationMember]:
        """Get member by user ID in organization."""
        try:
            return OrganizationMember.objects.get(
                organization_id=org_id,
                user_id=user_id
            )
        except OrganizationMember.DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get member by user: %s", e)
            raise
    
    def get_members(self, org_id: uuid.UUID) -> List[OrganizationMember]:
        """Get organization members."""
        try:
            return list(OrganizationMember.objects.filter(organization_id=org_id))
        except Exception as e:
            logger.error("Failed to get members: %s", e)
            raise
    
    
    def create_invite(self, data: Dict[str, Any]) -> Invite:
        """Create organization invite."""
        try:
            # Get the User instance for the inviter
            from django.contrib.auth import get_user_model
            User = get_user_model()
            inviter_user = User.objects.get(id=data['inviter_user_id'])
            
            invite = Invite.objects.create(
                invitee_email=data['invitee_email'],
                organization_id=data['org_id'],
                inviter=inviter_user,
                role=data.get('role', 'viewer'),
                secret=data['secret'],
                expires_at=data['expires_at']
            )
            logger.info("Created invite for %s to organization %s", data['invitee_email'], data['org_id'])
            return invite
        except Exception as e:
            logger.error("Failed to create invite: %s", e)
            raise
    
    def get_invite(self, **filters) -> Optional[Invite]:
        """Get invite by various filters (secret, invite_id, etc.)."""
        try:
            return Invite.objects.get(**filters)
        except Invite.DoesNotExist:
            return None
        except Exception as e:
            logger.error("Failed to get invite: %s", e)
            raise
    
    def get_invites(self, **filters) -> List[Invite]:
        """Get invites by various filters."""
        try:
            return list(Invite.objects.filter(**filters))
        except Exception as e:
            logger.error("Failed to get invites: %s", e)
            raise
    
    def update_invite_status(self, invite_id: uuid.UUID, used: bool) -> bool:
        """Update invite usage status."""
        try:
            invite = Invite.objects.get(invite_id=invite_id)
            invite.used = used
            invite.save()
            status = "used" if used else "unused"
            logger.info("Marked invite %s as %s", invite_id, status)
            return True
        except Invite.DoesNotExist:
            return False
        except Exception as e:
            logger.error("Failed to update invite status: %s", e)
            raise
    
    def reject_invite(self, invite_id: uuid.UUID) -> bool:
        """Reject invite by marking it as used (rejected)."""
        try:
            invite = Invite.objects.get(invite_id=invite_id)
            invite.used = True  # Mark as used to prevent further use
            invite.save()
            logger.info("Invite %s rejected by user", invite_id)
            return True
        except Invite.DoesNotExist:
            logger.warning("Invite %s not found for rejection", invite_id)
            return False
        except Exception as e:
            logger.error("Failed to reject invite: %s", e)
            raise
    
    def update_member_role(self, org_id: uuid.UUID, user_id: uuid.UUID, new_role: str) -> bool:
        """Update member role in organization."""
        try:
            member = OrganizationMember.objects.get(
                organization_id=org_id,
                user_id=user_id
            )
            member.role = new_role
            member.save()
            logger.info("Updated member %s role to %s in organization %s", user_id, new_role, org_id)
            return True
        except OrganizationMember.DoesNotExist:
            return False
        except Exception as e:
            logger.error("Failed to update member role: %s", e)
            raise
    
    
    def revoke_invite(self, invite_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Revoke invite (only by the user who sent it)."""
        try:
            invite = Invite.objects.get(
                invite_id=invite_id,
                inviter=user_id
            )
            invite.delete()
            logger.info("Revoked invite %s by user %s", invite_id, user_id)
            return True
        except Invite.DoesNotExist:
            return False
        except Exception as e:
            logger.error("Failed to revoke invite: %s", e)
            raise
