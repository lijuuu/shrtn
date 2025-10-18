"""
Namespace models for the URL shortener application.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Namespace(models.Model):
    """
    Namespace model for organizing short URLs.
    Matches the database schema: namespaces table
    """
    namespace_id = models.AutoField(primary_key=True, db_column='namespaceId')
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='namespaces',
        db_column='orgId'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_namespaces',
        db_column='createdByUserId'
    )
    name = models.CharField(_("Namespace Name"), max_length=255, unique=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        db_table = "namespaces"
        verbose_name = _("Namespace")
        verbose_name_plural = _("Namespaces")

    def __str__(self):
        return self.name
