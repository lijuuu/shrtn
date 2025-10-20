from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Organization,
    OrganizationMember,
    Invite,
    BulkUpload,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin configuration for Organization model."""
    
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'owner__email', 'owner__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('name', 'owner')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    """Admin configuration for OrganizationMember model."""
    
    list_display = ('user', 'organization', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__email', 'user__name', 'organization__name')
    readonly_fields = ('joined_at',)


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    """Admin configuration for Invite model."""
    
    list_display = ('invitee_email', 'organization', 'inviter', 'used', 'expires_at', 'created_at')
    list_filter = ('used', 'created_at', 'expires_at')
    search_fields = ('invitee_email', 'organization__name', 'inviter__email')
    readonly_fields = ('secret', 'created_at')


@admin.register(BulkUpload)
class BulkUploadAdmin(admin.ModelAdmin):
    """Admin configuration for BulkUpload model."""
    
    list_display = ('upload_id', 'user', 'organization', 'namespace', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'organization__name', 'namespace__name')
    readonly_fields = ('upload_id', 'created_at')
