"""
Health check endpoints for the application.
"""
import logging
from datetime import datetime
from typing import Dict, Any
import redis
import acsylla
import asyncio

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


def check_postgresql_connection() -> Dict[str, Any]:
    """Check PostgreSQL database connectivity."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return {
            'status': 'healthy',
            'message': 'PostgreSQL connection successful',
            'engine': settings.DATABASES['default']['ENGINE']
        }
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        return {
            'status': 'unhealthy',
            'message': f'PostgreSQL connection failed: {str(e)}'
        }


def check_redis_connection() -> Dict[str, Any]:
    """Check Redis connectivity."""
    try:
        # Parse Redis URL from CELERY_BROKER_URL
        redis_url = getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        r.ping()
        return {
            'status': 'healthy',
            'message': 'Redis connection successful',
            'url': redis_url
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            'status': 'unhealthy',
            'message': f'Redis connection failed: {str(e)}'
        }


def check_scylla_connection() -> Dict[str, Any]:
    """Check ScyllaDB connectivity."""
    try:
        # ScyllaDB connection parameters
        use_docker = getattr(settings, 'USE_DOCKER', 'no').lower()
        if use_docker in ['yes', 'true', '1']:
            scylla_hosts = ['scylla']
        else:
            scylla_hosts = ['127.0.0.1']
        
        async def _check_scylla():
            cluster = acsylla.create_cluster(scylla_hosts)
            session = await cluster.create_session()
            
            # Try to execute a simple query
            statement = acsylla.create_statement("SELECT now() FROM system.local")
            await session.execute(statement)
            await session.close()
        
        # Run the async check
        asyncio.run(_check_scylla())
        
        return {
            'status': 'healthy',
            'message': 'ScyllaDB connection successful',
            'hosts': scylla_hosts
        }
    except Exception as e:
        logger.error("ScyllaDB health check failed: %s", e)
        return {
            'status': 'unhealthy',
            'message': 'ScyllaDB connection failed: %s' % str(e)
        }


@never_cache
@require_http_methods(["GET"])
def health_check(request) -> JsonResponse:
    """
    Basic health check endpoint.
    
    Returns:
        JsonResponse: Status 200 with basic health info
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'hirethon',
        'version': '1.0.0'
    })


@never_cache
@require_http_methods(["GET"])
def health_detailed(request) -> JsonResponse:
    """
    Detailed health check endpoint with database connectivity.
    
    Returns:
        JsonResponse: Status 200 with detailed health info or 503 if unhealthy
    """
    health_data: Dict[str, Any] = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'hirethon',
        'version': '1.0.0',
        'checks': {}
    }
    
    # Check PostgreSQL connectivity
    postgres_check = check_postgresql_connection()
    health_data['checks']['postgresql'] = postgres_check
    if postgres_check['status'] == 'unhealthy':
        health_data['status'] = 'unhealthy'
    
    # Check Redis connectivity
    redis_check = check_redis_connection()
    health_data['checks']['redis'] = redis_check
    if redis_check['status'] == 'unhealthy':
        health_data['status'] = 'unhealthy'
    
    # Check ScyllaDB connectivity
    scylla_check = check_scylla_connection()
    health_data['checks']['scylla'] = scylla_check
    if scylla_check['status'] == 'unhealthy':
        health_data['status'] = 'unhealthy'
    
    # Check Django settings
    try:
        health_data['checks']['settings'] = {
            'status': 'healthy',
            'debug': settings.DEBUG,
            'allowed_hosts': settings.ALLOWED_HOSTS,
            'database_engine': settings.DATABASES['default']['ENGINE']
        }
    except Exception as e:
        logger.error(f"Settings health check failed: {e}")
        health_data['checks']['settings'] = {
            'status': 'unhealthy',
            'message': f'Settings check failed: {str(e)}'
        }
        health_data['status'] = 'unhealthy'
    
    # Determine HTTP status code
    status_code = 200 if health_data['status'] == 'healthy' else 503
    
    return JsonResponse(health_data, status=status_code)


@never_cache
@require_http_methods(["GET"])
def health_ready(request) -> JsonResponse:
    """
    Readiness check endpoint for Kubernetes/container orchestration.
    Checks all critical services (PostgreSQL, Redis, ScyllaDB).
    
    Returns:
        JsonResponse: Status 200 if ready, 503 if not ready
    """
    checks = {
        'postgresql': check_postgresql_connection(),
        'redis': check_redis_connection(),
        'scylla': check_scylla_connection()
    }
    
    # Check if all services are healthy
    all_healthy = all(check['status'] == 'healthy' for check in checks.values())
    
    if all_healthy:
        return JsonResponse({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': checks
        })
    else:
        return JsonResponse({
            'status': 'not_ready',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': checks
        }, status=503)


@never_cache
@require_http_methods(["GET"])
def health_live(request) -> JsonResponse:
    """
    Liveness check endpoint for Kubernetes/container orchestration.
    
    Returns:
        JsonResponse: Status 200 if alive
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    })
