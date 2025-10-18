"""
Analytics API views for URL and namespace analytics.
"""
import logging
import uuid
from django.http import HttpRequest, JsonResponse
from core.utils.response import APIResponse
from core.permissions.decorators import require_organization_permission, require_namespace_access

logger = logging.getLogger(__name__)

class AnalyticsView:
    """Analytics API views."""
    
    def __init__(self):
        self.service = None
    
    def _get_service(self):
        """Lazy initialization of analytics service."""
        if self.service is None:
            from core.dependencies.service_registry import service_registry
            self.service = service_registry.get_analytics_service()
        return self.service
    
    @require_organization_permission('can_view')
    @require_namespace_access()
    def get_url_analytics(self, request: HttpRequest, org_id: uuid.UUID, namespace: str, shortcode: str) -> JsonResponse:
        """Get analytics for a specific URL."""
        try:
            # Get namespace ID from namespace name
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return APIResponse.error(
                    message="Namespace not found",
                    status_code=404
                )
            
            namespace_id = namespace_obj.namespace_id
            
            # Get analytics service
            analytics_service = self._get_service()
            if not analytics_service:
                return APIResponse.error(
                    message="Analytics service not available",
                    status_code=503
                )
            
            # Get parameters
            days = int(request.GET.get('days', 30))
            time_filter = request.GET.get('time_filter', None)
            
            # Validate time filter
            valid_filters = ['1day', '3days', '7days', '30days']
            if time_filter and time_filter not in valid_filters:
                return APIResponse.error(
                    message=f"Invalid time_filter. Must be one of: {', '.join(valid_filters)}",
                    status_code=400
                )
            
            # Get analytics data
            analytics_data = analytics_service.get_url_analytics(namespace_id, shortcode, days, time_filter)
            
            return APIResponse.success(
                message="URL analytics retrieved successfully",
                data=analytics_data
            )
            
        except ValueError as e:
            return APIResponse.error(
                message="Invalid days parameter",
                status_code=400
            )
        except Exception as e:
            logger.error("Failed to get URL analytics: %s", e)
            return APIResponse.error(
                message="Failed to retrieve analytics",
                status_code=500
            )
    
    @require_organization_permission('can_view')
    @require_namespace_access()
    def get_namespace_analytics(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Get analytics for all URLs in a namespace."""
        try:
            # Get namespace ID from namespace name
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return APIResponse.error(
                    message="Namespace not found",
                    status_code=404
                )
            
            namespace_id = namespace_obj.namespace_id
            
            # Get analytics service
            analytics_service = self._get_service()
            if not analytics_service:
                return APIResponse.error(
                    message="Analytics service not available",
                    status_code=503
                )
            
            # Get parameters
            days = int(request.GET.get('days', 30))
            time_filter = request.GET.get('time_filter', None)
            
            # Validate time filter
            valid_filters = ['1day', '3days', '7days', '30days']
            if time_filter and time_filter not in valid_filters:
                return APIResponse.error(
                    message=f"Invalid time_filter. Must be one of: {', '.join(valid_filters)}",
                    status_code=400
                )
            
            # Get analytics data
            analytics_data = analytics_service.get_namespace_analytics(namespace_id, days, time_filter)
            
            return APIResponse.success(
                message="Namespace analytics retrieved successfully",
                data=analytics_data
            )
            
        except ValueError as e:
            return APIResponse.error(
                message="Invalid days parameter",
                status_code=400
            )
        except Exception as e:
            logger.error("Failed to get namespace analytics: %s", e)
            return APIResponse.error(
                message="Failed to retrieve analytics",
                status_code=500
            )
    
    @require_organization_permission('can_view')
    @require_namespace_access()
    def get_realtime_stats(self, request: HttpRequest, org_id: uuid.UUID, namespace: str) -> JsonResponse:
        """Get real-time statistics for a namespace."""
        try:
            # Get namespace ID from namespace name
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespace_obj = namespace_service.get_by_name(namespace)
            if not namespace_obj:
                return APIResponse.error(
                    message="Namespace not found",
                    status_code=404
                )
            
            namespace_id = namespace_obj.namespace_id
            
            # Get analytics service
            analytics_service = self._get_service()
            if not analytics_service:
                return APIResponse.error(
                    message="Analytics service not available",
                    status_code=503
                )
            
            # Get real-time stats
            stats_data = analytics_service.get_realtime_stats(namespace_id)
            
            return APIResponse.success(
                message="Real-time statistics retrieved successfully",
                data=stats_data
            )
            
        except Exception as e:
            logger.error("Failed to get real-time stats: %s", e)
            return APIResponse.error(
                message="Failed to retrieve real-time statistics",
                status_code=500
            )
    
    @require_organization_permission('can_view')
    def get_country_analytics(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Get country-based analytics across all namespaces in organization."""
        try:
            # Get analytics service
            analytics_service = self._get_service()
            if not analytics_service:
                return APIResponse.error(
                    message="Analytics service not available",
                    status_code=503
                )
            
            # Get parameters
            days = int(request.GET.get('days', 30))
            time_filter = request.GET.get('time_filter', None)
            
            # Validate time filter
            valid_filters = ['1day', '3days', '7days', '30days']
            if time_filter and time_filter not in valid_filters:
                return APIResponse.error(
                    message=f"Invalid time_filter. Must be one of: {', '.join(valid_filters)}",
                    status_code=400
                )
            
            # Get organization namespaces
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespaces = namespace_service.get_by_organization(org_id)
            
            if not namespaces:
                return APIResponse.success(
                    message="No analytics data available",
                    data={
                        'total_clicks': 0,
                        'countries': [],
                        'country_distribution': {},
                        'tier_counts': {'tier_1': 0, 'tier_2': 0, 'tier_3': 0, 'tier_4': 0},
                        'top_countries': [],
                        'period_days': days,
                        'time_filter': time_filter,
                        'namespaces_analyzed': 0
                    }
                )
            
            # Get namespace IDs
            namespace_ids = [ns.namespace_id for ns in namespaces]
            
            # Get country analytics with tiers
            analytics_data = analytics_service.get_country_analytics_with_tiers(
                namespace_ids, days, time_filter
            )
            
            return APIResponse.success(
                message="Country analytics retrieved successfully",
                data=analytics_data
            )
            
        except ValueError as e:
            return APIResponse.error(
                message="Invalid days parameter",
                status_code=400
            )
        except Exception as e:
            logger.error("Failed to get country analytics: %s", e)
            return APIResponse.error(
                message="Failed to retrieve country analytics",
                status_code=500
            )
    
    @require_organization_permission('can_view')
    def get_tier_analytics(self, request: HttpRequest, org_id: uuid.UUID) -> JsonResponse:
        """Get tier-based analytics for organization."""
        try:
            # Get analytics service
            analytics_service = self._get_service()
            if not analytics_service:
                return APIResponse.error(
                    message="Analytics service not available",
                    status_code=503
                )
            
            # Get parameters
            days = int(request.GET.get('days', 30))
            time_filter = request.GET.get('time_filter', None)
            
            # Validate time filter
            valid_filters = ['1day', '3days', '7days', '30days']
            if time_filter and time_filter not in valid_filters:
                return APIResponse.error(
                    message=f"Invalid time_filter. Must be one of: {', '.join(valid_filters)}",
                    status_code=400
                )
            
            # Get organization namespaces
            from core.dependencies.service_registry import service_registry
            namespace_service = service_registry.get_namespace_service()
            namespaces = namespace_service.get_by_organization(org_id)
            
            if not namespaces:
                return APIResponse.success(
                    message="No analytics data available",
                    data={
                        'tier_breakdown': {
                            'tier_1': {'count': 0, 'countries': [], 'total_clicks': 0},
                            'tier_2': {'count': 0, 'countries': [], 'total_clicks': 0},
                            'tier_3': {'count': 0, 'countries': [], 'total_clicks': 0},
                            'tier_4': {'count': 0, 'countries': [], 'total_clicks': 0}
                        },
                        'period_days': days,
                        'time_filter': time_filter,
                        'namespaces_analyzed': 0
                    }
                )
            
            # Get namespace IDs
            namespace_ids = [ns.namespace_id for ns in namespaces]
            
            # Get country analytics with tiers
            analytics_data = analytics_service.get_country_analytics_with_tiers(
                namespace_ids, days, time_filter
            )
            
            # Process tier breakdown
            tier_breakdown = {
                'tier_1': {'count': 0, 'countries': [], 'total_clicks': 0},
                'tier_2': {'count': 0, 'countries': [], 'total_clicks': 0},
                'tier_3': {'count': 0, 'countries': [], 'total_clicks': 0},
                'tier_4': {'count': 0, 'countries': [], 'total_clicks': 0}
            }
            
            for country_data in analytics_data.get('top_countries', []):
                tier = country_data.get('tier', 'tier_4')
                tier_breakdown[tier]['count'] += 1
                tier_breakdown[tier]['countries'].append({
                    'country': country_data['country'],
                    'clicks': country_data['clicks'],
                    'percentage': country_data['percentage']
                })
                tier_breakdown[tier]['total_clicks'] += country_data['clicks']
            
            return APIResponse.success(
                message="Tier analytics retrieved successfully",
                data={
                    'tier_breakdown': tier_breakdown,
                    'tier_counts': analytics_data.get('tier_counts', {}),
                    'total_clicks': analytics_data.get('total_clicks', 0),
                    'period_days': days,
                    'time_filter': time_filter,
                    'namespaces_analyzed': len(namespaces)
                }
            )
            
        except ValueError as e:
            return APIResponse.error(
                message="Invalid parameters",
                status_code=400
            )
        except Exception as e:
            logger.error("Failed to get tier analytics: %s", e)
            return APIResponse.error(
                message="Failed to retrieve tier analytics",
                status_code=500
            )
