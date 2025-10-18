"""
URL patterns for namespace endpoints.
"""
from django.urls import path
from .views import NamespaceView

# Create view instance
namespace_view = NamespaceView()

urlpatterns = [
    # Namespace CRUD operations
    path('organizations/<uuid:org_id>/namespaces/', namespace_view.list_namespaces, name='namespace-list'),
    path('organizations/<uuid:org_id>/namespaces/create/', namespace_view.create_namespace, name='namespace-create'),
    path('namespaces/<str:namespace>/', namespace_view.get_namespace, name='namespace-detail'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/update/', namespace_view.update_namespace, name='namespace-update'),
    path('organizations/<uuid:org_id>/namespaces/<str:namespace>/delete/', namespace_view.delete_namespace, name='namespace-delete'),
    
    # Namespace validation
    path('namespaces/check/<str:namespace>/', namespace_view.check_namespace_availability, name='namespace-check'),
]
