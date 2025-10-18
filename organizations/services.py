"""
Organization service for business logic.
"""
import logging
from typing import Optional, List, Dict, Any
from django.core.exceptions import ValidationError
from core.database.base import Service
from .repositories import OrganizationRepository
from .models import Organization, OrganizationMember, Invite
import secrets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OrganizationService(Service):
    """
    Service layer for Organization business logic.
    """
    def __init__(self, repository: OrganizationRepository):
        super().__init__(repository)
        self.repository = repository

    def create(self, data: Dict[str, Any]) -> Organization:
        """Create organization with business logic validation."""
        name = data.get('name', '')
        owner_id = data.get('owner_id')
        
        if not name or len(name.strip()) < 2:
            raise ValidationError("Organization name must be at least 2 characters")
        
        if not owner_id:
            raise ValidationError("Owner ID is required")
        
        # Check if user already owns an organization with this name
        existing_orgs = self.repository.list({'owner_id': owner_id})
        for org in existing_orgs:
            if org.name.lower() == name.lower():
                raise ValidationError("You already have an organization with this name")
        
        organization = self.repository.create({
            'name': name.strip(),
            'owner_id': owner_id
        })
        
        # Auto-add owner as admin member
        self.repository.add_member(organization.org_id, owner_id, {
            'can_view': True,
            'can_admin': True,
            'can_update': True
        })
        
        return organization

    def get_by_id(self, org_id: int) -> Optional[Organization]:
        """Get organization by ID."""
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        return self.repository.get_by_id(org_id)

    def update(self, org_id: int, data: Dict[str, Any]) -> Optional[Organization]:
        """Update organization."""
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        
        if 'name' in data:
            name = data['name']
            if not name or len(name.strip()) < 2:
                raise ValidationError("Organization name must be at least 2 characters")
            data['name'] = name.strip()
        
        return self.repository.update(org_id, data)

    def delete(self, org_id: int) -> bool:
        """Delete organization."""
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        return self.repository.delete(org_id)

    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Organization]:
        """List organizations with optional filters."""
        return self.repository.list(filters)

    def get_user_organizations(self, user_id: int) -> List[Organization]:
        """Get organizations where user is a member."""
        return self.repository.list({'user_id': user_id})

    def add_member(self, org_id: int, user_id: int, permissions: Dict[str, bool]) -> OrganizationMember:
        """Add member to organization with validation."""
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        
        if not user_id or user_id <= 0:
            raise ValidationError("Invalid user ID")
        
        # Check if user is already a member
        existing_permissions = self.repository.get_user_permissions(org_id, user_id)
        if existing_permissions:
            raise ValidationError("User is already a member of this organization")
        
        return self.repository.add_member(org_id, user_id, permissions)

    def remove_member(self, org_id: int, user_id: int) -> bool:
        """Remove member from organization."""
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        
        if not user_id or user_id <= 0:
            raise ValidationError("Invalid user ID")
        
        return self.repository.remove_member(org_id, user_id)

    def get_members(self, org_id: int) -> List[OrganizationMember]:
        """Get organization members."""
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        
        return self.repository.get_members(org_id)

    def get_user_permissions(self, org_id: int, user_id: int) -> Optional[Dict[str, bool]]:
        """Get user permissions in organization."""
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        
        if not user_id or user_id <= 0:
            raise ValidationError("Invalid user ID")
        
        return self.repository.get_user_permissions(org_id, user_id)

    def create_invite(self, data: Dict[str, Any]) -> Invite:
        """Create organization invite with validation."""
        invitee_email = data.get('invitee_email', '')
        org_id = data.get('org_id')
        inviter_user_id = data.get('inviter_user_id')
        
        if not invitee_email or '@' not in invitee_email:
            raise ValidationError("Invalid email format")
        
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        
        if not inviter_user_id or inviter_user_id <= 0:
            raise ValidationError("Invalid inviter user ID")
        
        # Check if user is already a member
        # This would require checking if email belongs to existing user
        # For now, we'll skip this check
        
        # Generate secret token
        secret = secrets.token_urlsafe(32)
        
        # Set expiration (7 days from now)
        expires_at = datetime.now() + timedelta(days=7)
        
        return self.repository.create_invite({
            'invitee_email': invitee_email.lower().strip(),
            'org_id': org_id,
            'inviter_user_id': inviter_user_id,
            'can_view': data.get('can_view', False),
            'can_admin': data.get('can_admin', False),
            'can_update': data.get('can_update', False),
            'secret': secret,
            'expires_at': expires_at
        })

    def get_invite_by_secret(self, secret: str) -> Optional[Invite]:
        """Get invite by secret token."""
        if not secret:
            raise ValidationError("Secret token is required")
        
        return self.repository.get_invite_by_secret(secret)

    def get_pending_invites(self, org_id: int) -> List[Invite]:
        """Get pending invites for organization."""
        if not org_id or org_id <= 0:
            raise ValidationError("Invalid organization ID")
        
        return self.repository.get_pending_invites(org_id)

    def accept_invite(self, invite_id: int, user_id: int) -> bool:
        """Accept organization invite."""
        if not invite_id or invite_id <= 0:
            raise ValidationError("Invalid invite ID")
        
        if not user_id or user_id <= 0:
            raise ValidationError("Invalid user ID")
        
        # Mark invite as used
        success = self.repository.mark_invite_used(invite_id)
        if not success:
            return False
        
        # Add user as member (this would need invite details)
        # For now, we'll just mark the invite as used
        return True
