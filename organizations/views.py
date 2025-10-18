"""
Organization views layer for handling HTTP requests with serializers.
"""
from typing import Dict, Any, Optional
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
import json

from core.dependencies.services import service_dependency
from .serializers import (
    OrganizationSerializer,
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
        self.service = service_dependency.get_organization_service()
    
    def list_organizations(self, request: HttpRequest) -> JsonResponse:
        """List user's organizations."""
        try:
            # Get user ID from request (would come from JWT in real implementation)
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 1
            
            filters = {'user_id': user_id}
            organizations = self.service.list(filters)
            
            serializer = OrganizationSerializer(organizations, many=True)
            return JsonResponse({
                'message': 'Organizations retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': {
                    'organizations': serializer.data,
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
                
                response_serializer = OrganizationSerializer(organization)
                return JsonResponse({
                    'message': 'Organization created successfully',
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
    
    def get_organization(self, request: HttpRequest, org_id: int) -> JsonResponse:
        """Get organization by ID."""
        try:
            organization = self.service.get_by_id(org_id)
            if not organization:
                return JsonResponse({
                    'message': 'Organization not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            serializer = OrganizationSerializer(organization)
            return JsonResponse({
                'message': 'Organization retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': serializer.data
            })
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
    
    def update_organization(self, request: HttpRequest, org_id: int) -> JsonResponse:
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
    
    def delete_organization(self, request: HttpRequest, org_id: int) -> JsonResponse:
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
    
    def get_members(self, request: HttpRequest, org_id: int) -> JsonResponse:
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
    
    def add_member(self, request: HttpRequest, org_id: int) -> JsonResponse:
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
    
    def remove_member(self, request: HttpRequest, org_id: int, user_id: int) -> JsonResponse:
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
    
    def create_invite(self, request: HttpRequest, org_id: int) -> JsonResponse:
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
    
    def get_pending_invites(self, request: HttpRequest, org_id: int) -> JsonResponse:
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