from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Namespace


@admin.register(Namespace)
class NamespaceAdmin(admin.ModelAdmin):
    """Admin configuration for Namespace model."""
    
    list_display = ('name', 'organization', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'organization__name', 'created_by__email')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {'fields': ('name', 'organization', 'created_by')}),
        (_('Timestamps'), {'fields': ('created_at',)}),
    )
