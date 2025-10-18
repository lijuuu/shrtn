"""
Standardized API response utilities for consistent frontend integration.
"""
from typing import Any, Dict, Optional, List
from django.http import JsonResponse
from django.core.paginator import Paginator
import logging

logger = logging.getLogger(__name__)

class APIResponse:
    """Standardized API response format."""
    
    @staticmethod
    def success(
        message: str = "Success",
        data: Any = None,
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None
    ) -> JsonResponse:
        """
        Create a successful API response.
        
        Args:
            message: Human-readable message
            data: Response payload
            status_code: HTTP status code
            meta: Additional metadata (pagination, etc.)
        """
        response_data = {
            "success": True,
            "message": message,
            "status_code": status_code,
            "payload": data,
            "meta": meta or {}
        }
        return JsonResponse(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str = "Error occurred",
        data: Any = None,
        status_code: int = 400,
        errors: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> JsonResponse:
        """
        Create an error API response.
        
        Args:
            message: Human-readable error message
            data: Error payload (validation errors, etc.)
            status_code: HTTP status code
            errors: List of specific error messages
            meta: Additional metadata
        """
        response_data = {
            "success": False,
            "message": message,
            "status_code": status_code,
            "payload": data,
            "errors": errors or [],
            "meta": meta or {}
        }
        return JsonResponse(response_data, status=status_code)
    
    @staticmethod
    def paginated(
        queryset,
        page: int = 1,
        per_page: int = 20,
        serializer_class=None,
        message: str = "Data retrieved successfully",
        **serializer_kwargs
    ) -> JsonResponse:
        """
        Create a paginated response.
        
        Args:
            queryset: Django queryset or list
            page: Page number
            per_page: Items per page
            serializer_class: Serializer class to use
            message: Success message
            **serializer_kwargs: Additional serializer arguments
        """
        try:
            paginator = Paginator(queryset, per_page)
            page_obj = paginator.get_page(page)
            
            # Serialize data if serializer provided
            if serializer_class:
                serializer = serializer_class(page_obj.object_list, many=True, **serializer_kwargs)
                data = serializer.data
            else:
                data = list(page_obj.object_list)
            
            meta = {
                "pagination": {
                    "current_page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "per_page": per_page,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous()
                }
            }
            
            return APIResponse.success(
                message=message,
                data=data,
                meta=meta
            )
            
        except Exception as e:
            logger.error("Pagination error: %s", e)
            return APIResponse.error(
                message="Pagination failed",
                status_code=500
            )

class PermissionContext:
    """Utility for adding permission context to responses."""
    
    @staticmethod
    def get_user_permissions_in_org(user_id, org_id, organization_service):
        """Get user permissions in organization."""
        try:
            return organization_service.get_user_permissions(org_id, user_id)
        except Exception:
            return None
    
    @staticmethod
    def add_permission_context(data, user_id, org_id, organization_service):
        """Add permission context to data."""
        if isinstance(data, list):
            for item in data:
                if hasattr(item, 'organization_id'):
                    permissions = PermissionContext.get_user_permissions_in_org(
                        user_id, item.organization_id, organization_service
                    )
                    item.user_permissions = permissions or {}
        elif hasattr(data, 'organization_id'):
            permissions = PermissionContext.get_user_permissions_in_org(
                user_id, data.organization_id, organization_service
            )
            data.user_permissions = permissions or {}
        
        return data
