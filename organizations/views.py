"""
Organization views layer for handling HTTP requests with serializers.
"""
import uuid
from typing import Dict, Any, Optional
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
import json

from core.dependencies.service_registry import service_registry
from core.permissions.decorators import require_organization_permission, require_organization_role
from core.utils.response import APIResponse
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
        self.service = service_registry.get_organization_service()
    
    def list_organizations(self, request: HttpRequest) -> JsonResponse:
        """List user's organizations with permissions."""
        try:
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 1
            
            filters = {'user_id': user_id}
            organizations = self.service.list(filters)
            
            # Use enhanced serializer with request context for permissions
            serializer = OrganizationWithPermissionsSerializer(
                organizations, 
                many=True, 
                context={'request': request}
            )
            
            return APIResponse.success(
                message="Organizations retrieved successfully",
                data=serializer.data,
                meta={
                    "count": len(serializer.data),
                    "user_id": str(user_id)
                }
            )
            
        except Exception as e:
            return APIResponse.error(
                message="Failed to retrieve organizations",
                status_code=500
            )
    
    def create_organization(self, request: HttpRequest) -> JsonResponse:
        """Create new organization."""
        try:
            data = json.loads(request.body)
            
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 1
            data['owner_id'] = user_id
            
            serializer = OrganizationCreateSerializer(data=data)
            if serializer.is_valid():
                organization = self.service.create(serializer.validated_data)
                
                # Use enhanced serializer with permissions
                response_serializer = OrganizationWithPermissionsSerializer(
                    organization,
                    context={'request': request}
                )
                return APIResponse.success(
                    message="Organization created successfully",
                    data=response_serializer.data,
                    status_code=201,
                    meta={
                        "user_role": "admin",  # Creator is always admin
                        "user_permissions": {
                            "can_view": True,
                            "can_update": True,
                            "can_admin": True
                        }
                    }
                )
            else:
                return APIResponse.error(
                    message="Validation failed",
                    data=serializer.errors,
                    status_code=400
                )
            
        except json.JSONDecodeError:
            return APIResponse.error(
                message="Invalid JSON format",
                status_code=400
            )
        except ValidationError as e:
            return APIResponse.error(
                message=str(e),
                status_code=400
            )
        except Exception as e:
            return APIResponse.error(
                message="Failed to create organization",
                status_code=500
            )
    
    @require_organization_permission('can_view')
    def get_organization(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Get organization by ID."""
        try:
            organization = self.service.get_by_id(org_id)
            if not organization:
                return APIResponse.error(
                    message="Organization not found",
                    status_code=404
                )
            
            # Use detailed serializer with permissions and members
            serializer = OrganizationDetailSerializer(
                organization,
                context={'request': request}
            )
            return APIResponse.success(
                message="Organization retrieved successfully",
                data=serializer.data
            )
            
        except Exception as e:
            return APIResponse.error(
                message="Failed to retrieve organization",
                status_code=500
            )
    
    @require_organization_permission('can_admin')
    def update_organization(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Update organization."""
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
    
    @require_organization_permission('can_admin')
    def delete_organization(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Delete organization."""
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
    
    @require_organization_permission('can_view')
    def get_members(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Get organization members."""
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
    
    @require_organization_permission('can_admin')
    def add_member(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Add member to organization."""
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
    
    @require_organization_permission('can_admin')
    def remove_member(self, request: HttpRequest, org_id: uuid.UUID, user_id: uuid.UUID) -> JsonResponse:
        """Remove member from organization."""
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
    
    @require_organization_permission('can_admin')
    def create_invite(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Create organization invite."""
        try:
            data = json.loads(request.body)
            data['org_id'] = org_id
            
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 1
            data['inviter_user_id'] = user_id
            
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
    
    @require_organization_permission('can_admin')
    def get_pending_invites(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Get pending invites for organization."""
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
        """Get invite details by token (public endpoint)."""
        try:
            if not token:
                return APIResponse.error(
                    message="Invite token is required",
                    status_code=400
                )
            
            # Get invite details
            invite = self.service.get_invite_by_secret(token)
            if not invite:
                return APIResponse.error(
                    message="Invalid or expired invite",
                    status_code=404
                )
            
            # Check if invite is expired
            from datetime import datetime
            if invite.expires_at and invite.expires_at < datetime.now():
                return APIResponse.error(
                    message="Invite has expired",
                    status_code=410
                )
            
            if invite.used:
                return APIResponse.error(
                    message="Invite has already been used",
                    status_code=410
                )
            
            # Get organization details
            organization = self.service.get_by_id(invite.organization_id)
            if not organization:
                return APIResponse.error(
                    message="Organization not found",
                    status_code=404
                )
            
            # Get inviter details
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                inviter = User.objects.get(id=invite.inviter_user_id)
                inviter_name = f"{inviter.first_name} {inviter.last_name}".strip() or inviter.username
            except User.DoesNotExist:
                inviter_name = "Unknown"
            
            # Prepare response data
            invite_data = {
                'invite_id': str(invite.invite_id),
                'invitee_email': invite.invitee_email,
                'organization': {
                    'org_id': str(organization.org_id),
                    'name': organization.name,
                    'description': organization.description
                },
                'inviter': {
                    'user_id': str(invite.inviter_user_id),
                    'name': inviter_name
                },
                'expires_at': invite.expires_at.isoformat() if invite.expires_at else None,
                'created_at': invite.created_at.isoformat() if hasattr(invite, 'created_at') else None,
                'permissions': {
                    'can_view': invite.can_view,
                    'can_update': invite.can_update,
                    'can_admin': invite.can_admin
                }
            }
            
            return APIResponse.success(
                message="Invite details retrieved successfully",
                data=invite_data
            )
            
        except Exception as e:
            logger.error("Failed to get invite details: %s", e)
            return APIResponse.error(
                message="Failed to retrieve invite details",
                status_code=500
            )

    def accept_invite(self, request: HttpRequest, token: str) -> JsonResponse:
        """Accept organization invite by token."""
        try:
            if not token:
                return APIResponse.error(
                    message="Invite token is required",
                    status_code=400
                )
            
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
            if not user_id:
                return APIResponse.error(
                    message="Authentication required to accept invite",
                    status_code=401
                )
            
            # Get invite details first
            invite = self.service.get_invite_by_secret(token)
            if not invite:
                return APIResponse.error(
                    message="Invalid or expired invite",
                    status_code=404
                )
            
            # Check if invite is expired
            from datetime import datetime
            if invite.expires_at and invite.expires_at < datetime.now():
                return APIResponse.error(
                    message="Invite has expired",
                    status_code=410
                )
            
            if invite.used:
                return APIResponse.error(
                    message="Invite has already been used",
                    status_code=410
                )
            
            # Accept the invite
            success = self.service.accept_invite(invite.invite_id, user_id)
            if not success:
                return APIResponse.error(
                    message="Failed to accept invite",
                    status_code=500
                )
            
            # Get organization details for response
            organization = self.service.get_by_id(invite.organization_id)
            
            return APIResponse.success(
                message="Invite accepted successfully",
                data={
                    'organization': {
                        'org_id': str(organization.org_id),
                        'name': organization.name,
                        'description': organization.description
                    },
                    'user_permissions': {
                        'can_view': invite.can_view,
                        'can_update': invite.can_update,
                        'can_admin': invite.can_admin
                    },
                    'user_role': 'admin' if invite.can_admin else 'editor' if invite.can_update else 'viewer'
                },
                status_code=200
            )
            
        except ValidationError as e:
            return APIResponse.error(
                message=str(e),
                status_code=400
            )
        except Exception as e:
            logger.error("Failed to accept invite: %s", e)
            return APIResponse.error(
                message="Failed to accept invite",
                status_code=500
            )