"""
User views layer for handling HTTP requests with serializers.
"""
import uuid
import logging
import secrets
import requests
from typing import Dict, Any, Optional
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .jwt_auth import JWTAuthentication
from .serializers import (
    UserPublicSerializer,
    UserListSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    PasswordChangeSerializer,
    AuthResponseSerializer,
    AuthStatusSerializer,
    GoogleLoginSerializer
)
from core.utils.org_name_generator import generate_org_name
from core.views.base import AuthenticatedView
from core.utils.response import (
    success_response,
    error_response,
    server_error_response
)

User = get_user_model()
logger = logging.getLogger(__name__)


class UserView(AuthenticatedView):
    """
    Controller for User-related HTTP endpoints.
    """
    
    def __init__(self):
        super().__init__()
        self.service = self.get_service('user')
    
    
    def list_users(self, request: HttpRequest) -> JsonResponse:
        """List all users using serializer."""
        # Check authentication using base class method
        auth_error = self.check_auth(request)
        if auth_error:
            return auth_error
        
        try:
            verified_only = request.GET.get('verified_only', 'false').lower() == 'true'
            filters = {'verified_only': verified_only} if verified_only else None
            users = self.service.list(filters)
            
            # Use serializer for consistent JSON response
            serializer = UserListSerializer(users, many=True)
            
            return self.success_response(
                message='Users retrieved successfully',
                data={
                    'users': serializer.data,
                    'count': len(serializer.data)
                }
            )
            
        except Exception as e:
            return self.handle_exception(e, "User listing")
    
    def search_users(self, request: HttpRequest) -> JsonResponse:
        """Search users by name using serializer."""
        # Check authentication using base class method
        auth_error = self.check_auth(request)
        if auth_error:
            return auth_error
        
        try:
            query = request.GET.get('q', '')
            if not query:
                return self.error_response(
                    message='Search query is required',
                    status_code=400
                )
            
            users = self.service.search_users(query)
            
            # Use serializer for consistent JSON response
            serializer = UserListSerializer(users, many=True)
            
            return self.success_response(
                message='Search completed successfully',
                data={
                    'users': serializer.data,
                    'count': len(serializer.data),
                    'query': query
                }
            )
            
        except ValidationError as e:
            return self.error_response(
                message=str(e),
                status_code=400
            )
        except Exception as e:
            return self.handle_exception(e, "User search")
    
    def google_login(self, request: HttpRequest) -> JsonResponse:
        """Get Google OAuth redirect URL."""
        try:
            # Check if request method is GET
            if request.method != 'GET':
                return error_response(
                    message='Method not allowed. Use GET.',
                    status_code=405
                )
            
            # Google OAuth configuration
            client_id = "your-google-client-id"  # Replace with your actual client ID
            redirect_uri = request.build_absolute_uri('/auth/google/callback/')
            scope = "openid email profile"
            state = secrets.token_urlsafe(32)  # CSRF protection
            
            # Store state in session for verification
            request.session['oauth_state'] = state
            
            # Build Google OAuth URL
            google_oauth_url = (
                f"https://accounts.google.com/o/oauth2/v2/auth?"
                f"client_id={client_id}&"
                f"redirect_uri={redirect_uri}&"
                f"scope={scope}&"
                f"response_type=code&"
                f"state={state}&"
                f"access_type=offline"
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Google OAuth URL generated',
                'oauth_url': google_oauth_url,
                'redirect_uri': redirect_uri,
                'state': state
            })
            
        except Exception as e:
            logger.error("Failed to generate Google OAuth URL: %s", e)
            return error_response('Failed to generate Google OAuth URL', 500)
    
    def google_callback(self, request: HttpRequest) -> JsonResponse:
        """Handle Google OAuth callback."""
        try:
            # Check if request method is GET
            if request.method != 'GET':
                return error_response(
                    message='Method not allowed. Use GET.',
                    status_code=405
                )
            
            # Get authorization code from callback
            code = request.GET.get('code')
            state = request.GET.get('state')
            error = request.GET.get('error')
            
            if error:
                return error_response(f'Google OAuth error: {error}', 400)
            
            if not code:
                return error_response('Authorization code not provided', 400)
            
            # Verify state parameter (CSRF protection)
            session_state = request.session.get('oauth_state')
            if not session_state or state != session_state:
                return error_response('Invalid state parameter', 400)
            
            # Exchange code for access token
            access_token = self._exchange_code_for_token(code, request)
            if not access_token:
                return error_response('Failed to exchange code for token', 400)
            
            # Get user info from Google
            user_info = self._get_google_user_info(access_token)
            if not user_info:
                return error_response('Failed to get user info from Google', 400)
            
            # Process the user info (same as before)
            return self._process_google_user(user_info)
            
        except Exception as e:
            logger.error("Failed to handle Google OAuth callback: %s", e)
            return error_response('Failed to handle Google OAuth callback', 500)
    
    def _exchange_code_for_token(self, code: str, request: HttpRequest) -> Optional[str]:
        """Exchange authorization code for access token."""
        try:
            import requests
            
            client_id = "your-google-client-id"  # Replace with your actual client ID
            client_secret = "your-google-client-secret"  # Replace with your actual client secret
            redirect_uri = request.build_absolute_uri('/auth/google/callback/')
            
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            response = requests.post(token_url, data=token_data)
            if response.status_code == 200:
                token_info = response.json()
                return token_info.get('access_token')
            
            logger.error("Failed to exchange code for token: %s", response.text)
            return None
            
        except Exception as e:
            logger.error("Failed to exchange code for token: %s", e)
            return None
    
    def _get_google_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google using access token."""
        try:
            import requests
            
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(user_info_url, headers=headers)
            if response.status_code == 200:
                return response.json()
            
            logger.error("Failed to get user info: %s", response.text)
            return None
            
        except Exception as e:
            logger.error("Failed to get user info: %s", e)
            return None
    
    def _process_google_user(self, user_info: Dict[str, Any]) -> JsonResponse:
        """Process Google user information and create/login user."""
        try:
            google_id = user_info.get('id')
            email = user_info.get('email')
            name = user_info.get('name')
            picture = user_info.get('picture')
            
            if not google_id or not email or not name:
                return error_response('Invalid user information from Google', 400)
            
            # Check if user exists by Google ID
            try:
                user = User.objects.get(google_id=google_id)
                logger.info("Google login: Existing user found by Google ID: %s", google_id)
            except User.DoesNotExist:
                # Check if user exists by email
                try:
                    user = User.objects.get(email=email)
                    # Update existing user with Google ID
                    user.google_id = google_id
                    user.save()
                    logger.info("Google login: Linked existing user with Google ID: %s", google_id)
                except User.DoesNotExist:
                    # Create new user
                    username = f"{email.split('@')[0]}_google"
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        name=name,
                        google_id=google_id,
                        verified=True
                    )
                    logger.info("Google login: Created new user with Google ID: %s", google_id)
            
            # Generate JWT token
            from users.jwt_auth import generate_jwt_token
            token = generate_jwt_token(user)
            
            # Get user's organizations
            from core.dependencies.service_registry import service_registry
            organization_service = service_registry.get_organization_service()
            user_organizations = organization_service.get_user_organizations(user.id)
            
            return success_response(
                message="Google login successful",
                data={
                    'user': {
                        'id': str(user.id),
                        'email': user.email,
                        'name': user.name,
                        'username': user.username,
                        'verified': user.verified,
                        'is_active': user.is_active,
                        'google_id': user.google_id,
                        'created_at': user.created_at.isoformat(),
                        'updated_at': user.updated_at.isoformat()
                    },
                    'tokens': {
                        'access_token': token,
                        'token_type': 'Bearer',
                        'expires_in': 86400
                    },
                    'organizations': [
                        {
                            'org_id': str(org.org_id),
                            'name': org.name,
                            'role': org.role
                        } for org in user_organizations
                    ]
                }
            )
            
        except Exception as e:
            logger.error("Failed to process Google user: %s", e)
            return error_response('Failed to process Google user', 500)
    
    def google_login_api(self, request: HttpRequest) -> JsonResponse:
        """Handle Google OAuth login via API (for programmatic access)."""
        try:
            # Check if request method is POST
            if request.method != 'POST':
                return error_response(
                    message='Method not allowed. Use POST.',
                    status_code=405
                )
            
            # Check if request body is empty
            if not request.body:
                return error_response(
                    message='Request body is required',
                    status_code=400
                )
            
            import json
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                return error_response(
                    message=f'Invalid JSON format: {str(e)}',
                    status_code=400
                )
            
            # Validate Google login data
            serializer = GoogleLoginSerializer(data=data)
            if not serializer.is_valid():
                return error_response(
                    message='Invalid Google login data',
                    status_code=400,
                    data={'errors': serializer.errors}
                )
            
            google_data = serializer.validated_data
            google_id = google_data['google_id']
            email = google_data['email']
            name = google_data['name']
            
            # Check if user exists by Google ID
            try:
                user = User.objects.get(google_id=google_id)
                logger.info("Google login: Existing user found by Google ID: %s", google_id)
            except User.DoesNotExist:
                # Check if user exists by email
                try:
                    user = User.objects.get(email=email)
                    # Update existing user with Google ID
                    user.google_id = google_id
                    user.save()
                    logger.info("Google login: Updated existing user with Google ID: %s", google_id)
                except User.DoesNotExist:
                    # Create new user
                    username = email.split('@')[0] + '_google'
                    # Ensure username is unique
                    counter = 1
                    original_username = username
                    while User.objects.filter(username=username).exists():
                        username = f"{original_username}_{counter}"
                        counter += 1
                    
                    user = User.objects.create(
                        email=email,
                        name=name,
                        username=username,
                        google_id=google_id,
                        verified=True,
                        is_active=True
                    )
                    logger.info("Google login: Created new user with Google ID: %s", google_id)
            
            # Generate JWT token
            access_token = JWTAuthentication.generate_token(user)
            tokens = {
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': 86400  # 24 hours
            }
            
            # Get user's organizations
            from core.dependencies.service_registry import service_registry
            organization_service = service_registry.get_organization_service()
            user_organizations = organization_service.get_user_organizations(user.id)
            
            # Serialize organizations
            organizations_data = []
            for org in user_organizations:
                organizations_data.append({
                    'org_id': str(org.org_id),
                    'name': org.name,
                    'role': 'admin'  # User is admin of their own organizations
                })
            
            # Serialize user data
            user_serializer = UserProfileSerializer(user)
            
            return success_response(
                message='Google login successful',
                data={
                    'user': user_serializer.data,
                    'tokens': tokens,
                    'organizations': organizations_data
                }
            )
            
        except json.JSONDecodeError:
            return error_response(
                message='Invalid JSON format',
                status_code=400
            )
        except Exception as e:
            logger.error("Google login error: %s", e)
            return server_error_response('Google login failed')
    
