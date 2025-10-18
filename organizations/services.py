"""
Organization service for business logic.
"""
import uuid
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
        
        # Basic validation
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

    def get_by_id(self, org_id: uuid.UUID) -> Optional[Organization]:
        """Get organization by ID."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        return self.repository.get_by_id(org_id)

    def update(self, org_id: uuid.UUID, data: Dict[str, Any]) -> Optional[Organization]:
        """Update organization."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        if 'name' in data:
            name = data['name']
            if not name or len(name.strip()) < 2:
                raise ValidationError("Organization name must be at least 2 characters")
            data['name'] = name.strip()
        
        return self.repository.update(org_id, data)

    def delete(self, org_id: uuid.UUID) -> bool:
        """Delete organization with cascade delete for namespaces and URLs."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        try:
            # Get organization info before deletion
            organization = self.repository.get_by_id(org_id)
            if not organization:
                return False
            
            # Get namespace service to handle cascade deletion
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            
            # Delete all namespaces in this organization
            try:
                namespaces_in_org = namespace_service.get_by_organization(org_id)
                for namespace in namespaces_in_org:
                    # This will cascade delete all URLs in the namespace
                    namespace_service.delete(namespace.namespace_id)
                    logger.info("Deleted namespace %s from organization %s", namespace.name, organization.name)
            except Exception as namespace_error:
                logger.warning("Failed to delete namespaces for organization %s: %s", organization.name, namespace_error)
                # Continue with organization deletion even if namespace deletion fails
            
            # Delete organization from PostgreSQL
            success = self.repository.delete(org_id)
            
            if success:
                logger.info("Deleted organization %s and all associated namespaces and URLs", organization.name)
            
            return success
            
        except Exception as e:
            logger.error("Failed to delete organization: %s", e)
            raise

    def list(self, filters: Optional[Dict[str, Any]] = None) -> List[Organization]:
        """List organizations with optional filters."""
        return self.repository.list(filters)

    def get_user_organizations(self, user_id: uuid.UUID) -> List[Organization]:
        """Get organizations where user is a member."""
        return self.repository.list({'user_id': user_id})

    def add_member(self, org_id: uuid.UUID, user_id: uuid.UUID, permissions: Dict[str, bool]) -> OrganizationMember:
        """Add member to organization with validation."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        # Check if user is already a member
        existing_permissions = self.repository.get_user_permissions(org_id, user_id)
        if existing_permissions:
            raise ValidationError("User is already a member of this organization")
        
        return self.repository.add_member(org_id, user_id, permissions)

    def remove_member(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Remove member from organization."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        return self.repository.remove_member(org_id, user_id)

    def get_members(self, org_id: uuid.UUID) -> List[OrganizationMember]:
        """Get organization members."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        return self.repository.get_members(org_id)

    def get_user_permissions(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Dict[str, bool]]:
        """Get user permissions in organization."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        return self.repository.get_user_permissions(org_id, user_id)

    def create_invite(self, data: Dict[str, Any]) -> Invite:
        """Create organization invite with validation and email sending."""
        invitee_email = data.get('invitee_email', '')
        org_id = data.get('org_id')
        inviter_user_id = data.get('inviter_user_id')
        
        if not invitee_email or '@' not in invitee_email:
            raise ValidationError("Invalid email format")
        
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        if not inviter_user_id:
            raise ValidationError("Invalid inviter user ID")
        
        # Get organization and inviter details for email
        organization = self.repository.get_by_id(org_id)
        if not organization:
            raise ValidationError("Organization not found")
        
        # Get inviter details
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            inviter = User.objects.get(id=inviter_user_id)
            inviter_name = f"{inviter.first_name} {inviter.last_name}".strip() or inviter.username
        except User.DoesNotExist:
            raise ValidationError("Inviter not found")
        
        # Check if user is already a member
        # This would require checking if email belongs to existing user
        # For now, we'll skip this check
        
        # Generate secret token
        secret = secrets.token_urlsafe(32)
        
        # Set expiration (7 days from now)
        expires_at = datetime.now() + timedelta(days=7)
        
        # Create invite in database
        invite = self.repository.create_invite({
            'invitee_email': invitee_email.lower().strip(),
            'org_id': org_id,
            'inviter_user_id': inviter_user_id,
            'can_view': data.get('can_view', False),
            'can_admin': data.get('can_admin', False),
            'can_update': data.get('can_update', False),
            'secret': secret,
            'expires_at': expires_at
        })
        
        # Send email invitation
        try:
            from core.dependencies.service_registry import service_registry
            
            email_service = service_registry.get_email_service()
            if not email_service:
                logger.warning("Email service not available, skipping email send")
                return invite
            
            # Create invite URL (this would be your frontend URL)
            invite_url = f"http://localhost:3000/invite/{secret}"  # Adjust to your frontend URL
            
            # Format expiration date
            expires_at_formatted = expires_at.strftime('%B %d, %Y at %I:%M %p')
            
            # Send email
            email_sent = email_service.send_organization_invite(
                invitee_email=invitee_email,
                organization_name=organization.name,
                inviter_name=inviter_name,
                invite_url=invite_url,
                expires_at=expires_at_formatted
            )
            
            if email_sent:
                logger.info("Invitation email sent successfully to %s", invitee_email)
            else:
                logger.warning("Failed to send invitation email to %s", invitee_email)
                # Don't fail the invite creation if email fails
                
        except Exception as e:
            logger.error("Failed to send invitation email: %s", e)
            # Don't fail the invite creation if email fails
        
        return invite

    def get_invite_by_secret(self, secret: str) -> Optional[Invite]:
        """Get invite by secret token."""
        if not secret:
            raise ValidationError("Secret token is required")
        
        return self.repository.get_invite_by_secret(secret)

    def get_pending_invites(self, org_id: uuid.UUID) -> List[Invite]:
        """Get pending invites for organization."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        return self.repository.get_pending_invites(org_id)

    def accept_invite(self, invite_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Accept organization invite."""
        if not invite_id:
            raise ValidationError("Invalid invite ID")
        
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        try:
            # Get invite details first
            invite = self.repository.get_invite_by_id(invite_id)
            if not invite:
                raise ValidationError("Invite not found")
            
            if invite.used:
                raise ValidationError("Invite has already been used")
            
            if invite.expires_at and invite.expires_at < datetime.now():
                raise ValidationError("Invite has expired")
            
            # Check if user is already a member
            existing_permissions = self.repository.get_user_permissions(invite.organization_id, user_id)
            if existing_permissions:
                raise ValidationError("User is already a member of this organization")
            
            # Mark invite as used
            success = self.repository.mark_invite_used(invite_id)
            if not success:
                return False
            
            # Add user to organization with default permissions
            default_permissions = {
                'can_view': True,
                'can_update': False,  # Can be customized based on invite type
                'can_admin': False
            }
            
            # Add member to organization
            member = self.repository.add_member(invite.organization_id, user_id, default_permissions)
            if not member:
                # Rollback invite usage if member addition fails
                self.repository.mark_invite_unused(invite_id)
                return False
            
            logger.info("User %s accepted invite and joined organization %s", user_id, invite.organization_id)
            return True
            
        except Exception as e:
            logger.error("Failed to accept invite: %s", e)
            raise
