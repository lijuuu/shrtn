"""
Authentication views moved from authentication app to users app.
"""
import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .jwt_auth import JWTAuthentication
from core.utils.org_name_generator import generate_org_name
from core.utils.view_helpers import get_service
from core.utils.response import (
    success_response, 
    error_response, 
    validation_error_response,
    unauthorized_response,
    server_error_response,
    created_response
)

User = get_user_model()
logger = logging.getLogger(__name__)

# Create a single JWT authentication instance to reuse
jwt_auth = JWTAuthentication()


def authenticate_user(request):
    """
    Helper function to authenticate user using JWT.
    Returns (user, token) tuple if authenticated, None if not.
    """
    try:
        return jwt_auth.authenticate(request)
    except Exception as e:
        logger.error("JWT authentication failed: %s", e)
        return None


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """
    Register a new user with email and password.
    """
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        organization_name = data.get('organization_name', '').strip()
        
        # Validation
        if not email:
            return error_response('Email is required', 400)
        
        if not password or len(password) < 8:
            return error_response('Password must be at least 8 characters', 400)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return error_response('Invalid email format', 400)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return error_response('User with this email already exists', 400)
        
        # Create user with auto-verification
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name.split()[0] if name else '',
            last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
            verified=True  # Auto-verify users for now
        )
        
        # Create default organization
        organization_service = get_service('organization')
        
        # Use custom organization name or generate random one
        org_name = organization_name if organization_name else generate_org_name()
        
        org_data = {
            'name': org_name,
            'owner_id': user.id
        }
        organization = organization_service.create(org_data)
        
        logger.info("New user registered: %s with organization: %s", user.email, organization.name)
        
        # Generate JWT tokens
        access_token = JWTAuthentication.generate_token(user)
        jwt_tokens = {
            'access': access_token,
            'refresh': access_token
        }
        
        return created_response('User registered successfully', {
            'user': {
                'id': str(user.id),
                'email': user.email,
                'name': user.get_full_name(),
                'verified': user.verified
            },
            'organization': {
                'id': str(organization.org_id),
                'name': organization.name
            },
            'tokens': jwt_tokens
        })
        
    except Exception as e:
        logger.error("Registration failed: %s", e)
        return server_error_response('Registration failed')


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """
    Login user with email and password.
    """
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return error_response('Email and password are required', 400)
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if not user:
            return unauthorized_response('Invalid credentials')
        
        if not user.is_active:
            return unauthorized_response('Account is disabled')
        
        # Generate JWT tokens
        access_token = JWTAuthentication.generate_token(user)
        jwt_tokens = {
            'access': access_token,
            'refresh': access_token
        }
        
        return success_response('Login successful', {
            'user': {
                'id': str(user.id),
                'email': user.email,
                'name': user.get_full_name(),
                'verified': user.verified
            },
            'tokens': jwt_tokens
        })
        
    except Exception as e:
        logger.error("Login failed: %s", e)
        return server_error_response('Login failed')


@csrf_exempt
@require_http_methods(["GET"])
def get_profile(request):
    """
    Get user profile using JWT authentication.
    """
    try:
        # Use JWT authentication
        auth_result = authenticate_user(request)
        
        if not auth_result:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required',
                'status_code': 401,
                'payload': None
            }, status=401)
        
        user, token = auth_result
        
        # Get user organizations
        organizations = []
        try:
            org_service = get_service('organization')
            user_orgs = org_service.get_user_organizations(user.id)
            organizations = [
                {
                    'id': str(org.org_id),
                    'name': org.name,
                    'role': 'admin'  # User is admin of their own organizations
                } for org in user_orgs
            ]
        except Exception as e:
            logger.warning("Failed to load user organizations: %s", e)
        
        return JsonResponse({
            'success': True,
            'message': 'Profile retrieved successfully',
            'status_code': 200,
            'payload': {
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'name': user.get_full_name(),
                    'username': user.username,
                    'verified': user.verified,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
                    'updated_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None
                },
                'organizations': organizations
            }
        })
        
    except Exception as e:
        logger.error("Profile retrieval failed: %s", e)
        return JsonResponse({
            'success': False,
            'message': 'Profile retrieval failed',
            'status_code': 500,
            'payload': None,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_profile(request):
    """
    Update user profile using JWT authentication.
    """
    try:
        # Use JWT authentication
        auth_result = authenticate_user(request)
        
        if not auth_result:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required',
                'status_code': 401,
                'payload': None
            }, status=401)
        
        user, token = auth_result
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
        if name:
            name_parts = name.split()
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully',
            'status_code': 200,
            'payload': {
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'name': user.get_full_name(),
                    'username': user.username,
                    'verified': user.verified,
                    'is_active': user.is_active
                }
            }
        })
        
    except Exception as e:
        logger.error("Profile update failed: %s", e)
        return JsonResponse({
            'success': False,
            'message': 'Profile update failed',
            'status_code': 500,
            'payload': None,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def change_password(request):
    """
    Change user password using JWT authentication.
    """
    try:
        # Use JWT authentication
        auth_result = authenticate_user(request)
        
        if not auth_result:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required',
                'status_code': 401,
                'payload': None
            }, status=401)
        
        user, token = auth_result
        data = json.loads(request.body)
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return JsonResponse({
                'success': False,
                'message': 'Current password and new password are required',
                'status_code': 400,
                'payload': None
            }, status=400)
        
        # Verify current password
        if not user.check_password(current_password):
            return JsonResponse({
                'success': False,
                'message': 'Current password is incorrect',
                'status_code': 400,
                'payload': None
            }, status=400)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully',
            'status_code': 200,
            'payload': None
        })
        
    except Exception as e:
        logger.error("Password change failed: %s", e)
        return JsonResponse({
            'success': False,
            'message': 'Password change failed',
            'status_code': 500,
            'payload': None,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def auth_status(request):
    """
    Check authentication status using JWT authentication.
    """
    try:
        # Use JWT authentication instead of session auth
        auth_result = authenticate_user(request)
        
        if auth_result:
            user, token = auth_result
            
            # Get user organizations using service layer
            organizations = []
            try:
                org_service = get_service('organization')
                user_orgs = org_service.get_user_organizations(user.id)
                organizations = [
                    {
                        'id': str(org.org_id),
                        'name': org.name,
                        'role': 'admin'  # User is admin of their own organizations
                    } for org in user_orgs
                ]
            except Exception as e:
                logger.warning("Failed to load user organizations: %s", e)
            
            # Generate fresh JWT tokens
            access_token = JWTAuthentication.generate_token(user)
            jwt_tokens = {
                'access': access_token,
                'refresh': access_token
            }
            
            return JsonResponse({
                'success': True,
                'message': 'User is authenticated',
                'status_code': 200,
                'payload': {
                    'authenticated': True,
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'name': user.get_full_name(),
                        'username': user.username,
                        'verified': user.verified,
                        'is_active': user.is_active,
                        'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
                        'updated_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else None
                    },
                    'organizations': organizations,
                    'tokens': jwt_tokens
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'User is not authenticated',
                'status_code': 200,
                'payload': {
                    'authenticated': False,
                    'user': None,
                    'tokens': None
                }
            })
            
    except Exception as e:
        logger.error("Auth status check failed: %s", e)
        return JsonResponse({
            'success': False,
            'message': 'Auth status check failed',
            'status_code': 500,
            'payload': None,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    """
    Logout user.
    """
    try:
        # Django's logout function
        from django.contrib.auth import logout as django_logout
        django_logout(request)
        
        return JsonResponse({
            'success': True,
            'message': 'Logged out successfully',
            'status_code': 200,
            'payload': None
        })
        
    except Exception as e:
        logger.error("Logout failed: %s", e)
        return JsonResponse({
            'success': False,
            'message': 'Logout failed',
            'status_code': 500,
            'payload': None,
            'error': str(e)
        }, status=500)
