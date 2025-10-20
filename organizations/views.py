"""
Organization views layer for handling HTTP requests with serializers.
"""
import uuid
import logging
from typing import Dict, Any, Optional
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
import json

logger = logging.getLogger(__name__)

from core.utils.view_helpers import get_service, get_authenticated_user
from core.utils.response import (
    success_response, 
    error_response, 
    created_response,
    unauthorized_response,
    not_found_response,
    server_error_response
)
from .serializers import (
    OrganizationSerializer,
    OrganizationWithPermissionsSerializer,
    OrganizationDetailSerializer,
    OrganizationCreateSerializer,
    OrganizationMemberSerializer,
    OrganizationMemberCreateSerializer,
    InviteSerializer,
    InviteCreateSerializer
)


class OrganizationView:
    """
    Organization views for HTTP endpoints.
    """
    
    def __init__(self):
        self.service = get_service('organization')
    
    def list_organizations(self, request: HttpRequest) -> JsonResponse:
        """List user's organizations with permissions."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            filters = {'user_id': user.id}
            organizations = self.service.list(filters)
            
            # Use enhanced serializer with request context for permissions
            serializer = OrganizationWithPermissionsSerializer(
                organizations, 
                many=True, 
                context={'request': request}
            )
            
            return success_response(
                message="Organizations retrieved successfully",
                data={
                    "organizations": serializer.data,
                    "count": len(serializer.data),
                    "user_id": str(user.id)
                }
            )
            
        except Exception as e:
            return server_error_response(f"Failed to retrieve organizations: {str(e)}")
    
    @csrf_exempt
    def create_organization(self, request: HttpRequest) -> JsonResponse:
        """Create new organization."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            data = json.loads(request.body)
            
            # Use authenticated user ID from JWT (convert UUID to string)
            data['owner'] = str(user.id)
            
            serializer = OrganizationCreateSerializer(data=data)
            if serializer.is_valid():
                organization = self.service.create(serializer.validated_data)
                
                # Use enhanced serializer with permissions
                response_serializer = OrganizationWithPermissionsSerializer(
                    organization,
                    context={'request': request}
                )
                return created_response(
                    message="Organization created successfully",
                    data={
                        "organization": response_serializer.data,
                        "user_role": "admin"  # Creator is always admin
                    }
                )
            else:
                return error_response(
                    message="Validation failed",
                    status_code=400,
                    data=serializer.errors
                )
            
        except json.JSONDecodeError:
            return error_response(
                message="Invalid JSON format",
                status_code=400
            )
        except ValidationError as e:
            # Handle ValidationError with clean message
            error_message = str(e)
            return error_response(
                message=error_message,
                status_code=400
            )
        except Exception as e:
            return error_response(
                message=f"Failed to create organization: {str(e)}",
                status_code=500
            )
    
    def get_organization(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Get organization by ID."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            organization = self.service.get_by_id(org_id)
            if not organization:
                return error_response(
                    message="Organization not found",
                    status_code=404
                )
            
            # Use detailed serializer with permissions and members
            serializer = OrganizationDetailSerializer(
                organization,
                context={'request': request}
            )
            return success_response(
                message="Organization retrieved successfully",
                data=serializer.data
            )
            
        except Exception as e:
            return error_response(
                message="Failed to retrieve organization",
                status_code=500
            )
    
    @csrf_exempt
    def update_organization(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Update organization."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            data = json.loads(request.body)
            
            serializer = OrganizationCreateSerializer(data=data, partial=True)
            if serializer.is_valid():
                updated_organization = self.service.update(org_id, serializer.validated_data)
                if not updated_organization:
                    return JsonResponse({
                        'message': 'Organization not found',
                        'status_code': 404,
                        'success': False,
                        'payload': None
                    }, status=404)
                
                response_serializer = OrganizationSerializer(updated_organization)
                return JsonResponse({
                    'message': 'Organization updated successfully',
                    'status_code': 200,
                    'success': True,
                    'payload': response_serializer.data
                })
            else:
                return JsonResponse({
                    'message': 'Validation failed',
                    'status_code': 400,
                    'success': False,
                    'payload': {
                        'errors': serializer.errors
                    }
                }, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'message': 'Invalid JSON format',
                'status_code': 400,
                'success': False,
                'payload': None
            }, status=400)
        except ValidationError as e:
            return JsonResponse({
                'message': str(e),
                'status_code': 400,
                'success': False,
                'payload': None
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    @csrf_exempt
    def delete_organization(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Delete organization."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            success = self.service.delete(org_id)
            if not success:
                return JsonResponse({
                    'message': 'Organization not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            return JsonResponse({
                'message': 'Organization deleted successfully',
                'status_code': 200,
                'success': True,
                'payload': None
            })
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    def get_members(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Get organization members."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            members = self.service.get_members(org_id)
            
            serializer = OrganizationMemberSerializer(members, many=True)
            return JsonResponse({
                'message': 'Members retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': {
                    'members': serializer.data,
                    'count': len(serializer.data)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    @csrf_exempt
    def add_member(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Add member to organization."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            data = json.loads(request.body)
            
            serializer = OrganizationMemberCreateSerializer(data=data)
            if serializer.is_valid():
                member = self.service.add_member(org_id, **serializer.validated_data)
                
                response_serializer = OrganizationMemberSerializer(member)
                return JsonResponse({
                    'message': 'Member added successfully',
                    'status_code': 201,
                    'success': True,
                    'payload': response_serializer.data
                }, status=201)
            else:
                return JsonResponse({
                    'message': 'Validation failed',
                    'status_code': 400,
                    'success': False,
                    'payload': {
                        'errors': serializer.errors
                    }
                }, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'message': 'Invalid JSON format',
                'status_code': 400,
                'success': False,
                'payload': None
            }, status=400)
        except ValidationError as e:
            return JsonResponse({
                'message': str(e),
                'status_code': 400,
                'success': False,
                'payload': None
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    @csrf_exempt
    def remove_member(self, request: HttpRequest, org_id: uuid.UUID, user_id: uuid.UUID) -> JsonResponse:
        """Remove member from organization."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            success = self.service.remove_member(org_id, user_id)
            if not success:
                return JsonResponse({
                    'message': 'Member not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            return JsonResponse({
                'message': 'Member removed successfully',
                'status_code': 200,
                'success': True,
                'payload': None
            })
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    @csrf_exempt
    def create_invite(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Create organization invite."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            data = json.loads(request.body)
            data['org_id'] = org_id
            
            # Use authenticated user ID from JWT
            data['inviter_user_id'] = user.id
            
            serializer = InviteCreateSerializer(data=data)
            if serializer.is_valid():
                invite = self.service.create_invite(serializer.validated_data)
                
                response_serializer = InviteSerializer(invite)
                return JsonResponse({
                    'message': 'Invite created successfully',
                    'status_code': 201,
                    'success': True,
                    'payload': response_serializer.data
                }, status=201)
            else:
                return JsonResponse({
                    'message': 'Validation failed',
                    'status_code': 400,
                    'success': False,
                    'payload': {
                        'errors': serializer.errors
                    }
                }, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'message': 'Invalid JSON format',
                'status_code': 400,
                'success': False,
                'payload': None
            }, status=400)
        except ValidationError as e:
            return JsonResponse({
                'message': str(e),
                'status_code': 400,
                'success': False,
                'payload': None
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    def get_pending_invites(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Get pending invites for organization."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            invites = self.service.get_pending_invites(org_id)
            
            serializer = InviteSerializer(invites, many=True)
            return JsonResponse({
                'message': 'Pending invites retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': {
                    'invites': serializer.data,
                    'count': len(serializer.data)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
        
    def get_invite_details(self, request: HttpRequest, token: str) -> JsonResponse:
        """Get invite details by token or invite ID (public endpoint)."""
        try:
            if not token:
                return error_response(
                    message="Invite token is required",
                    status_code=400
                )
            
            # Try to get invite by secret first, then by invite_id
            invite = self.service.get_invite_by_secret(token)
            if not invite:
                # If not found by secret, try by invite_id (UUID)
                try:
                    import uuid
                    invite_id = uuid.UUID(token)
                    invite = self.service.repository.get_invite(invite_id=invite_id)
                except (ValueError, TypeError):
                    # Not a valid UUID, so it's not an invite_id either
                    pass
            
            if not invite:
                return error_response(
                    message="Invalid invite",
                    status_code=404
                )
            
            # Check if invite is expired
            from django.utils import timezone
            if invite.expires_at and invite.expires_at < timezone.now():
                return error_response(
                    message="Invite has expired",
                    status_code=410
                )
            
            if invite.used:
                return error_response(
                    message="Invite has already been used",
                    status_code=410
                )
            
            # Get organization details
            organization = self.service.get_by_id(invite.organization_id)
            if not organization:
                return error_response(
                    message="Organization not found",
                    status_code=404
                )
            
            # Get inviter details
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                inviter = User.objects.get(id=invite.inviter_id)
                inviter_name = f"{inviter.first_name} {inviter.last_name}".strip() or inviter.username
            except User.DoesNotExist:
                inviter_name = "Unknown"
            
            # Prepare response data
            invite_data = {
                'invite_id': str(invite.invite_id),
                'invitee_email': invite.invitee_email,
                'organization': {
                    'org_id': str(organization.org_id),
                    'name': organization.name
                },
                'inviter': {
                    'user_id': str(invite.inviter_id),
                    'name': inviter_name
                },
                'expires_at': invite.expires_at.isoformat() if invite.expires_at else None,
                'created_at': invite.created_at.isoformat() if hasattr(invite, 'created_at') else None,
                'role': invite.role
            }
            
            return success_response(
                message="Invite details retrieved successfully",
                data=invite_data
            )
            
        except Exception as e:
            logger.error("Failed to get invite details: %s", e)
            return error_response(
                message="Failed to retrieve invite details",
                status_code=500
            )

    @csrf_exempt
    def accept_invite(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Accept organization invite by organization ID and user ID."""
        try:
            # Check if user is authenticated
            user = get_authenticated_user(request)
            if not user:
                return error_response(
                    message="Please log in to accept this invite",
                    status_code=401
                )
            
            # Check if organization exists
            organization = self.service.get_by_id(org_id)
            if not organization:
                return error_response(
                    message="Organization not found",
                    status_code=404
                )
            
            # Check if user is already a member
            existing_member = self.service.repository.get_member_by_user(org_id, user.id)
            if existing_member:
                return error_response(
                    message="User is already a member of this organization",
                    status_code=400
                )
            
            # Add user to organization with default role
            member = self.service.repository.add_member(org_id, user.id, 'viewer')
            if not member:
                return error_response(
                    message="Failed to add user to organization",
                    status_code=500
                )
            
            logger.info("User %s joined organization %s", user.id, org_id)
            
            return success_response(
                message="Successfully joined organization",
                data={
                    'organization': {
                        'org_id': str(organization.org_id),
                        'name': organization.name
                    },
                    'user_role': 'viewer'
                },
                status_code=200
            )
            
        except ValidationError as e:
            return error_response(
                message=str(e),
                status_code=400
            )
        except Exception as e:
            logger.error("Failed to accept invite: %s", e)
            return error_response(
                message="Failed to accept invite",
                status_code=500
            )
    
    def get_sent_invites(self, request: HttpRequest) -> JsonResponse:
        """Get invites sent by the current user."""
        # Check authentication
        user = get_authenticated_user(request)
        if not user:
            return unauthorized_response('Authentication required')
        
        try:
            invites = self.service.get_sent_invites(user.id)
            
            serializer = InviteSerializer(invites, many=True)
            return success_response(
                message='Sent invites retrieved successfully',
                data={
                    'invites': serializer.data,
                    'count': len(serializer.data)
                }
            )
            
        except Exception as e:
            return server_error_response('Failed to retrieve sent invites')
    
    def get_received_invites(self, request: HttpRequest) -> JsonResponse:
        """Get invites received by the current user."""
        try:
            user = get_authenticated_user(request)
            if not user:
                return unauthorized_response('Authentication required')
            
            invites = self.service.get_received_invites(user.email)
            
            serializer = InviteSerializer(invites, many=True)
            return success_response(
                message='Received invites retrieved successfully',
                data={
                    'invites': serializer.data,
                    'count': len(serializer.data)
                }
            )
            
        except Exception as e:
            return server_error_response('Failed to retrieve received invites')
    
    @csrf_exempt
    def revoke_invite(self, request: HttpRequest, invite_id: uuid.UUID) -> JsonResponse:
        """Revoke a sent invite."""
        try:
            user = get_authenticated_user(request)
            if not user:
                return unauthorized_response('Authentication required')
            
            success = self.service.revoke_invite(invite_id, user.id)
            if not success:
                return not_found_response('Invite not found or you do not have permission to revoke it')
            
            return success_response('Invite revoked successfully')
            
        except Exception as e:
            return server_error_response('Failed to revoke invite')
    
    @csrf_exempt
    def reject_invite(self, request: HttpRequest, invite_id: uuid.UUID) -> JsonResponse:
        """Reject an organization invite."""
        try:
            user = get_authenticated_user(request)
            if not user:
                return unauthorized_response('Authentication required')
            
            success = self.service.reject_invite(invite_id)
            if not success:
                return not_found_response('Invite not found or already used')
            
            logger.info("User %s rejected invite %s", user.id, invite_id)
            
            return success_response(
                message='Invite rejected successfully',
                data={
                    'invite_id': str(invite_id),
                    'status': 'rejected'
                }
            )
            
        except ValidationError as e:
            return error_response(
                message=str(e),
                status_code=400
            )
        except Exception as e:
            logger.error("Failed to reject invite: %s", e)
            return server_error_response('Failed to reject invite')
    
    @csrf_exempt
    def update_member_role(self, request: HttpRequest, org_id: uuid.UUID, user_id: uuid.UUID) -> JsonResponse:
        """Update member role in organization."""
        try:
            user = get_authenticated_user(request)
            if not user:
                return unauthorized_response('Authentication required')
            
            data = json.loads(request.body)
            new_role = data.get('role')
            
            if not new_role:
                return error_response('Role is required', 400)
            
            # Validate role
            valid_roles = ['viewer', 'editor', 'admin']
            if new_role not in valid_roles:
                return error_response(f'Invalid role. Must be one of: {valid_roles}', 400)
            
            # Check if user has admin permissions
            if not self.service.has_admin_permission(org_id, user.id):
                return error_response('Admin permissions required', 403)
            
            success = self.service.update_member_role(org_id, user_id, new_role)
            if not success:
                return not_found_response('Member not found')
            
            return success_response('Member role updated successfully')
            
        except json.JSONDecodeError:
            return error_response('Invalid JSON format', 400)
        except Exception as e:
            return server_error_response('Failed to update member role')
    