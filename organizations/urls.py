"""
URL patterns for organization endpoints.
"""
from django.urls import path
from .views import OrganizationView

# Create view instance
org_view = OrganizationView()

urlpatterns = [
    # Organization CRUD operations
    path('organizations/', org_view.list_organizations, name='organization-list'),
    path('organizations/create/', org_view.create_organization, name='organization-create'),
    path('organizations/<uuid:org_id>/', org_view.get_organization, name='organization-detail'),
    path('organizations/<uuid:org_id>/update/', org_view.update_organization, name='organization-update'),
    path('organizations/<uuid:org_id>/delete/', org_view.delete_organization, name='organization-delete'),
    
    # Organization members
    path('organizations/<uuid:org_id>/members/', org_view.get_members, name='organization-members'),
    path('organizations/<uuid:org_id>/members/add/', org_view.add_member, name='organization-add-member'),
    path('organizations/<uuid:org_id>/members/<uuid:user_id>/remove/', org_view.remove_member, name='organization-remove-member'),
    
    # Organization invites
    path('organizations/<uuid:org_id>/invites/', org_view.get_pending_invites, name='organization-invites'),
    path('organizations/<uuid:org_id>/invites/create/', org_view.create_invite, name='organization-create-invite'),

    # Public invite endpoints (no authentication required for getting details)
    path('invites/<str:token>/', org_view.get_invite_details, name='invite-details'),
    path('invites/<str:token>/accept/', org_view.accept_invite, name='invite-accept'),
]
