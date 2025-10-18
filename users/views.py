"""
User views layer for handling HTTP requests with serializers.
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
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer,
    UserPublicSerializer,
    UserListSerializer
)


class UserView:
    """
    Controller for User-related HTTP endpoints.
    """
    
    def __init__(self):
        self.service = service_dependency.get_user_service()
    
    def get_user(self, request: HttpRequest, user_id: int) -> JsonResponse:
        """Get user by ID using serializer."""
        try:
            user = self.service.get_by_id(user_id)
            if not user:
                return JsonResponse({
                    'message': 'User not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            # Use serializer for consistent JSON response
            serializer = UserSerializer(user)
            return JsonResponse({
                'message': 'User retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': serializer.data
            })
            
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
    
    def get_user_by_email(self, request: HttpRequest, email: str) -> JsonResponse:
        """Get user by email using serializer."""
        try:
            user = self.service.get_by_email(email)
            if not user:
                return JsonResponse({
                    'message': 'User not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            # Use serializer for consistent JSON response
            serializer = UserSerializer(user)
            return JsonResponse({
                'message': 'User retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': serializer.data
            })
            
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
    
    def create_user(self, request: HttpRequest) -> JsonResponse:
        """Create a new user using serializer."""
        try:
            data = json.loads(request.body)
            
            # Use serializer for validation and creation
            serializer = UserCreateSerializer(data=data)
            if serializer.is_valid():
                user = self.service.create(serializer.validated_data)
                
                # Return created user data using UserSerializer
                response_serializer = UserSerializer(user)
                return JsonResponse({
                    'message': 'User created successfully',
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
    
    def update_user(self, request: HttpRequest, user_id: int) -> JsonResponse:
        """Update user using serializer."""
        try:
            data = json.loads(request.body)
            
            # Use serializer for validation and update
            serializer = UserUpdateSerializer(data=data, partial=True)
            if serializer.is_valid():
                updated_user = self.service.update(user_id, serializer.validated_data)
                if not updated_user:
                    return JsonResponse({
                        'message': 'User not found',
                        'status_code': 404,
                        'success': False,
                        'payload': None
                    }, status=404)
                
                # Return updated user data
                response_serializer = UserSerializer(updated_user)
                return JsonResponse({
                    'message': 'User updated successfully',
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
    
    def delete_user(self, request: HttpRequest, user_id: int) -> JsonResponse:
        """Delete user."""
        try:
            success = self.service.delete(user_id)
            if not success:
                return JsonResponse({
                    'message': 'User not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            return JsonResponse({
                'message': 'User deleted successfully',
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
    
    def list_users(self, request: HttpRequest) -> JsonResponse:
        """List all users using serializer."""
        try:
            verified_only = request.GET.get('verified_only', 'false').lower() == 'true'
            filters = {'verified_only': verified_only} if verified_only else None
            users = self.service.list(filters)
            
            # Use serializer for consistent JSON response
            serializer = UserListSerializer(users, many=True)
            
            return JsonResponse({
                'message': 'Users retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': {
                    'users': serializer.data,
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
    
    def search_users(self, request: HttpRequest) -> JsonResponse:
        """Search users by name using serializer."""
        try:
            query = request.GET.get('q', '')
            if not query:
                return JsonResponse({
                    'message': 'Search query is required',
                    'status_code': 400,
                    'success': False,
                    'payload': None
                }, status=400)
            
            users = self.service.search_users(query)
            
            # Use serializer for consistent JSON response
            serializer = UserListSerializer(users, many=True)
            
            return JsonResponse({
                'message': 'Search completed successfully',
                'status_code': 200,
                'success': True,
                'payload': {
                    'users': serializer.data,
                    'count': len(serializer.data),
                    'query': query
                }
            })
            
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
    
    def get_user_stats(self, request: HttpRequest, user_id: int) -> JsonResponse:
        """Get user statistics."""
        try:
            stats = self.service.get_user_stats(user_id)
            if not stats:
                return JsonResponse({
                    'message': 'User not found',
                    'status_code': 404,
                    'success': False,
                    'payload': None
                }, status=404)
            
            return JsonResponse({
                'message': 'User statistics retrieved successfully',
                'status_code': 200,
                'success': True,
                'payload': {
                    'stats': stats
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'message': 'Internal server error',
                'status_code': 500,
                'success': False,
                'payload': None
            }, status=500)
