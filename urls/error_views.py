"""
Error page views for URL redirection scenarios.
"""
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def url_not_found(request):
    """404 page for URL not found."""
    return render(request, 'urls/404.html', {
        'title': 'URL Not Found',
        'message': 'The short URL you are looking for does not exist.',
        'status_code': 404
    }, status=404)


@csrf_exempt
@require_http_methods(["GET"])
def url_inactive(request):
    """Page for inactive URLs."""
    return render(request, 'urls/inactive.html', {
        'title': 'URL Inactive',
        'message': 'This short URL is currently inactive.',
        'status_code': 410
    }, status=410)


@csrf_exempt
@require_http_methods(["GET"])
def url_expired(request):
    """Page for expired URLs."""
    return render(request, 'urls/expired.html', {
        'title': 'URL Expired',
        'message': 'This short URL has expired.',
        'status_code': 410
    }, status=410)


@csrf_exempt
@require_http_methods(["GET"])
def server_error(request):
    """500 page for server errors."""
    return render(request, 'urls/500.html', {
        'title': 'Server Error',
        'message': 'An error occurred while processing your request.',
        'status_code': 500
    }, status=500)
