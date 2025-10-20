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
        owner_id = data.get('owner_id') or data.get('owner')  # Support both field names
        
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
        # Add owner as member with admin role
        self.repository.add_member(organization.org_id, owner_id, 'admin')
        
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

    def add_member(self, org_id: uuid.UUID, user_id: uuid.UUID, role: str = 'viewer') -> OrganizationMember:
        """Add member to organization with role."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        # Validate role
        valid_roles = ['viewer', 'editor', 'admin']
        if role not in valid_roles:
            raise ValidationError(f"Invalid role. Must be one of: {valid_roles}")
        
        # Check if user is already a member
        existing_member = self.repository.get_member_by_user(org_id, user_id)
        if existing_member:
            raise ValidationError("User is already a member of this organization")
        
        return self.repository.add_member(org_id, user_id, role)

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
        
        member = self.repository.get_member_by_user(org_id, user_id)
        if member:
            # Convert role to permission flags for backward compatibility
            role = member.role
            return {
                'role': role,
                'can_view': role in ['viewer', 'editor', 'admin'],
                'can_update': role in ['editor', 'admin'],
                'can_admin': role == 'admin'
            }
        return None
    
    def get_member_by_user(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Optional[OrganizationMember]:
        """Get member by user ID in organization."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        return self.repository.get_member_by_user(org_id, user_id)
    
    def update_member_role(self, org_id: uuid.UUID, user_id: uuid.UUID, new_role: str) -> bool:
        """Update member role in organization."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        # Validate role
        valid_roles = ['viewer', 'editor', 'admin']
        if new_role not in valid_roles:
            raise ValidationError(f"Invalid role. Must be one of: {valid_roles}")
        
        return self.repository.update_member_role(org_id, user_id, new_role)
    
    def has_admin_permission(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user has admin permission in organization."""
        member = self.get_member_by_user(org_id, user_id)
        return member and member.role == 'admin'
    
    def has_edit_permission(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user has edit permission in organization."""
        member = self.get_member_by_user(org_id, user_id)
        return member and member.role in ['editor', 'admin']
    
    def has_view_permission(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user has view permission in organization."""
        member = self.get_member_by_user(org_id, user_id)
        return member and member.role in ['viewer', 'editor', 'admin']

    def create_invite(self, data: Dict[str, Any]) -> Invite:
        """Create organization invite with validation and email sending."""
        invitee_email = data.get('invitee_email', '')
        org_id = data.get('org_id')
        inviter_user_id = data.get('inviter_user_id')
        
        logger.info("Creating invite - Email: %s, Org ID: %s, Inviter: %s", 
                   invitee_email, org_id, inviter_user_id)
        
        if not invitee_email or '@' not in invitee_email:
            raise ValidationError("Invalid email format")
        
        if not org_id:
            logger.error("Invalid organization ID: %s", org_id)
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
            'role': data.get('role', 'viewer'),
            'secret': secret,
            'expires_at': expires_at
        })
        
        # Send email invitation
        try:
            from core.utils.view_helpers import get_service
            
            email_service = get_service('email')
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
        
        return self.repository.get_invite(secret=secret)

    def get_pending_invites(self, org_id: uuid.UUID) -> List[Invite]:
        """Get pending invites for organization."""
        if not org_id:
            raise ValidationError("Invalid organization ID")
        
        return self.repository.get_invites(organization_id=org_id, used=False)

    def accept_invite(self, invite_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Accept organization invite."""
        if not invite_id:
            raise ValidationError("Invalid invite ID")
        
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        try:
            # Get invite details first
            invite = self.repository.get_invite(invite_id=invite_id)
            if not invite:
                raise ValidationError("Invite not found")
            
            if invite.used:
                raise ValidationError("Invite has already been used")
            
            
            # Check if user is already a member
            existing_member = self.repository.get_member_by_user(invite.organization_id, user_id)
            if existing_member:
                raise ValidationError("User is already a member of this organization")
            
            # Mark invite as used
            success = self.repository.update_invite_status(invite_id, used=True)
            if not success:
                return False
            
            # Add user to organization with role from invite
            role = getattr(invite, 'role', 'viewer')  # Default to viewer if no role specified
            
            # Add member to organization
            member = self.repository.add_member(invite.organization_id, user_id, role)
            if not member:
                # Rollback invite usage if member addition fails
                self.repository.update_invite_status(invite_id, used=False)
                return False
            
            logger.info("User %s accepted invite and joined organization %s", user_id, invite.organization_id)
            return True
            
        except Exception as e:
            logger.error("Failed to accept invite: %s", e)
            raise
    
    def get_sent_invites(self, user_id: uuid.UUID) -> List[Invite]:
        """Get invites sent by user."""
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        return self.repository.get_invites(inviter=user_id)
    
    def get_received_invites(self, email: str) -> List[Invite]:
        """Get invites received by email."""
        if not email or '@' not in email:
            raise ValidationError("Invalid email format")
        
        return self.repository.get_invites(invitee_email=email.lower(), used=False)
    
    def revoke_invite(self, invite_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Revoke invite (only by the user who sent it)."""
        if not invite_id:
            raise ValidationError("Invalid invite ID")
        
        if not user_id:
            raise ValidationError("Invalid user ID")
        
        return self.repository.revoke_invite(invite_id, user_id)
    
    def reject_invite(self, invite_id: uuid.UUID) -> bool:
        """Reject invite by the invitee."""
        if not invite_id:
            raise ValidationError("Invalid invite ID")
        
        return self.repository.reject_invite(invite_id)