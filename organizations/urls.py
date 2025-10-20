"""
URL patterns for organization management endpoints.
"""
from django.urls import path
from .views import OrganizationView

# Create view instance
org_view = OrganizationView()

urlpatterns = [
    # Organization management endpoints
    path('', org_view.list_organizations, name='org-list'),
    path('create/', org_view.create_organization, name='org-create'),
    path('<uuid:org_id>/', org_view.get_organization, name='org-detail'),
    path('<uuid:org_id>/update/', org_view.update_organization, name='org-update'),
    path('<uuid:org_id>/delete/', org_view.delete_organization, name='org-delete'),
    
    # Member management endpoints
    path('<uuid:org_id>/members/', org_view.get_members, name='org-members'),
    # path('<uuid:org_id>/members/add/', org_view.add_member, name='org-add-member'),
    path('<uuid:org_id>/members/<uuid:user_id>/remove/', org_view.remove_member, name='org-remove-member'),
    # path('<uuid:org_id>/members/<uuid:user_id>/role/', org_view.update_member_role, name='org-update-member-role'),
    
    # Invite management endpoints
    path('<uuid:org_id>/invites/create/', org_view.create_invite, name='org-create-invite'),
    path('<uuid:org_id>/invites/', org_view.get_pending_invites, name='org-pending-invites'),
    path('invites/sent/', org_view.get_sent_invites, name='org-sent-invites'),
    path('invites/received/', org_view.get_received_invites, name='org-received-invites'),
    path('invites/<uuid:invite_id>/revoke/', org_view.revoke_invite, name='org-revoke-invite'),
    path('invites/<uuid:invite_id>/reject/', org_view.reject_invite, name='org-reject-invite'),
    path('invites/<str:token>/details/', org_view.get_invite_details, name='org-invite-details'),
    path('invites/<uuid:org_id>/accept/', org_view.accept_invite, name='org-accept-invite'),
]