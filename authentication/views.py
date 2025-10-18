"""
Authentication views for login, register, SSO, and callbacks.
"""
import logging
import secrets
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, authenticate, get_user_model
from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
from urllib.parse import urlencode
from .jwt_auth import JWTAuthentication
from core.utils.org_name_generator import generate_org_name

User = get_user_model()

logger = logging.getLogger(__name__)


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
            return JsonResponse({
                'error': 'Email is required'
            }, status=400)
        
        if not password or len(password) < 8:
            return JsonResponse({
                'error': 'Password must be at least 8 characters'
            }, status=400)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'error': 'Invalid email format'
            }, status=400)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'error': 'User with this email already exists'
            }, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name.split()[0] if name else '',
            last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
            verified=False  # Email verification required
        )
        
        # Create default organization
        from core.dependencies.service_registry import service_registry
        organization_service = service_registry.get_organization_service()
        
        # Use custom organization name or generate random one
        org_name = organization_name if organization_name else generate_org_name()
        
        org_data = {
            'name': org_name,
            'owner_id': user.id,
            'description': f"Default organization for {user.email}"
        }
        organization = organization_service.create(org_data)
        
        logger.info("New user registered: %s with organization: %s", user.email, organization.name)
        
        # Generate JWT tokens
        access_token = JWTAuthentication.generate_token(user)
        jwt_tokens = {
            'access': access_token,
            'refresh': access_token
        }
        
        return JsonResponse({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.get_full_name(),
                'verified': user.verified
            },
            'organization': {
                'id': organization.org_id,
                'name': organization.name
            },
            'tokens': jwt_tokens
        }, status=201)
        
    except Exception as e:
        logger.error("Registration failed: %s", e)
        return JsonResponse({
            'error': 'Registration failed',
            'message': str(e)
        }, status=500)


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
        
        # Validation
        if not email or not password:
            return JsonResponse({
                'error': 'Email and password are required'
            }, status=400)
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return JsonResponse({
                'error': 'Invalid credentials'
            }, status=401)
        
        if not user.is_active:
            return JsonResponse({
                'error': 'Account is disabled'
            }, status=401)
        
        # Login user
        login(request, user)
        
        # Generate JWT tokens
        access_token = JWTAuthentication.generate_token(user)
        jwt_tokens = {
            'access': access_token,
            'refresh': access_token
        }
        
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.get_full_name(),
                'verified': user.verified
            },
            'tokens': jwt_tokens
        })
        
    except Exception as e:
        logger.error("Login failed: %s", e)
        return JsonResponse({
            'error': 'Login failed',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def google_login(request):
    """
    Initiate Google OAuth login.
    Redirects user to Google OAuth consent screen.
    """
    try:
        # Google OAuth parameters
        params = {
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'scope': 'openid email profile',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        # Build Google OAuth URL
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        
        return redirect(auth_url)
        
    except Exception as e:
        logger.error("Google login initiation failed: %s", e)
        return JsonResponse({
            'error': 'Authentication failed',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def google_callback(request):
    """
    Handle Google OAuth callback.
    Exchange authorization code for access token and user info.
    """
    try:
        # Get authorization code from callback
        code = request.GET.get('code')
        error = request.GET.get('error')
        
        if error:
            logger.error("Google OAuth error: %s", error)
            return JsonResponse({
                'error': 'OAuth authentication failed',
                'message': error
            }, status=400)
        
        if not code:
            return JsonResponse({
                'error': 'Authorization code not provided'
            }, status=400)
        
        # Exchange code for access token
        token_data = {
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        }
        
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if token_response.status_code != 200:
            logger.error("Token exchange failed: %s", token_response.text)
            return JsonResponse({
                'error': 'Token exchange failed',
                'message': token_response.text
            }, status=400)
        
        token_info = token_response.json()
        access_token = token_info.get('access_token')
        
        # Get user info from Google
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_info_response.status_code != 200:
            logger.error("User info fetch failed: %s", user_info_response.text)
            return JsonResponse({
                'error': 'Failed to fetch user information'
            }, status=400)
        
        user_info = user_info_response.json()
        
        # Create or get user
        user, created = User.objects.get_or_create(
            email=user_info['email'],
            defaults={
                'username': user_info['email'],
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
                'is_active': True,
                'verified': True,  # Google verified email
            }
        )
        
        if created:
            logger.info("New user created via Google OAuth: %s", user.email)
            # Create default organization for new user
            from core.dependencies.service_registry import service_registry
            organization_service = service_registry.get_organization_service()
            
            # Generate random organization name
            org_name = generate_org_name()
            
            org_data = {
                'name': org_name,
                'owner_id': user.id,
                'description': f"Default organization for {user.email}"
            }
            organization = organization_service.create(org_data)
            logger.info("Default organization '%s' created for user '%s'", organization.name, user.email)
        
        # Login user
        login(request, user)
        
        # Generate JWT tokens
        access_token = JWTAuthentication.generate_token(user)
        jwt_tokens = {
            'access': access_token
        }
        
        return JsonResponse({
            'success': True,
            'message': 'Authentication successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'verified': user.verified
            },
            'tokens': jwt_tokens
        })
        
    except Exception as e:
        logger.error("Google OAuth callback failed: %s", e)
        return JsonResponse({
            'error': 'Authentication failed',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def auth_status(request):
    """
    Check authentication status and return user info.
    """
    try:
        if request.user.is_authenticated:
            # Generate fresh JWT tokens
            access_token = JWTAuthentication.generate_token(request.user)
            jwt_tokens = {
                'access': access_token,
                'refresh': access_token
            }
            
            return JsonResponse({
                'authenticated': True,
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'name': f"{request.user.first_name} {request.user.last_name}".strip(),
                    'verified': request.user.verified
                },
                'tokens': jwt_tokens
            })
        else:
            return JsonResponse({
                'authenticated': False,
                'user': None
            })
            
    except Exception as e:
        logger.error("Auth status check failed: %s", e)
        return JsonResponse({
            'error': 'Failed to check authentication status',
            'message': str(e)
        }, status=500)


@require_http_methods(["POST"])
def logout(request):
    """
    Logout user and invalidate session.
    """
    try:
        from django.contrib.auth import logout as django_logout
        django_logout(request)
        
        return JsonResponse({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        logger.error("Logout failed: %s", e)
        return JsonResponse({
            'error': 'Logout failed',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def refresh_token(request):
    """
    Refresh JWT token.
    """
    try:
        data = json.loads(request.body)
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return JsonResponse({
                'error': 'Refresh token is required'
            }, status=400)
        
        # Decode and validate refresh token
        try:
            payload = JWTAuthentication().decode_token(refresh_token)
            user_id = payload.get('user_id')
            
            if not user_id:
                return JsonResponse({
                    'error': 'Invalid refresh token'
                }, status=401)
            
            user = User.objects.get(id=user_id)
            
            # Generate new access token
            new_access_token = JWTAuthentication.generate_token(user)
            
            return JsonResponse({
                'success': True,
                'access_token': new_access_token
            })
            
        except User.DoesNotExist:
            return JsonResponse({
                'error': 'User not found'
            }, status=401)
        except Exception as e:
            logger.error("Token refresh failed: %s", e)
            return JsonResponse({
                'error': 'Invalid refresh token'
            }, status=401)
            
    except Exception as e:
        logger.error("Token refresh failed: %s", e)
        return JsonResponse({
            'error': 'Token refresh failed',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def change_password(request):
    """
    Change user password.
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required'
            }, status=401)
        
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return JsonResponse({
                'error': 'Current password and new password are required'
            }, status=400)
        
        if len(new_password) < 8:
            return JsonResponse({
                'error': 'New password must be at least 8 characters'
            }, status=400)
        
        # Verify current password
        if not request.user.check_password(current_password):
            return JsonResponse({
                'error': 'Current password is incorrect'
            }, status=400)
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        logger.info("Password changed for user: %s", request.user.email)
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        logger.error("Password change failed: %s", e)
        return JsonResponse({
            'error': 'Password change failed',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_profile(request):
    """
    Update user profile.
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required'
            }, status=401)
        
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        
        if name:
            name_parts = name.split()
            request.user.first_name = name_parts[0] if name_parts else ''
            request.user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully',
            'user': {
                'id': request.user.id,
                'email': request.user.email,
                'name': request.user.get_full_name(),
                'verified': request.user.verified
            }
        })
        
    except Exception as e:
        logger.error("Profile update failed: %s", e)
        return JsonResponse({
            'error': 'Profile update failed',
            'message': str(e)
        }, status=500)