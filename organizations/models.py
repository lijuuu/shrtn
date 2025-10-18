"""
Organization models for the URL shortener application.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Organization(models.Model):
    """
    Organization model for managing groups of users.
    """
    org_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='orgId')
    name = models.CharField(_("Organization Name"), max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_organizations',
        db_column='ownerId'
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        db_table = "organizations"
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    """
    Organization membership model for managing user permissions.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
        db_column='orgId'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        db_column='userId'
    )
    can_view = models.BooleanField(_("Can View"), default=False)
    can_admin = models.BooleanField(_("Can Admin"), default=False)
    can_update = models.BooleanField(_("Can Update"), default=False)
    joined_at = models.DateTimeField(_("Joined At"), auto_now_add=True)

    class Meta:
        db_table = "organization_members"
        verbose_name = _("Organization Member")
        verbose_name_plural = _("Organization Members")
        unique_together = ['organization', 'user']

    def __str__(self):
        return f"{self.user.email} in {self.organization.name}"


class Invite(models.Model):
    """
    Organization invitation model.
    """
    invite_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='inviteId')
    invitee_email = models.EmailField(_("Invitee Email"))
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invites',
        db_column='orgId'
    )
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_invites',
        db_column='inviter_userId'
    )
    can_view = models.BooleanField(_("Can View"), default=False)
    can_admin = models.BooleanField(_("Can Admin"), default=False)
    can_update = models.BooleanField(_("Can Update"), default=False)
    used = models.BooleanField(_("Used"), default=False)
    secret = models.CharField(_("Secret"), max_length=255, unique=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    expires_at = models.DateTimeField(_("Expires At"))

    class Meta:
        db_table = "invites"
        verbose_name = _("Invite")
        verbose_name_plural = _("Invites")

    def __str__(self):
        return f"Invite for {self.invitee_email} to {self.organization.name}"


class BulkUpload(models.Model):
    """
    Bulk upload model for managing bulk URL uploads.
    """
    STATUS_CHOICES = [
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]

    upload_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_column='uploadId')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bulk_uploads',
        db_column='userId'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='bulk_uploads',
        db_column='orgId'
    )
    namespace = models.ForeignKey(
        'namespaces.Namespace',
        on_delete=models.CASCADE,
        related_name='bulk_uploads',
        db_column='namespaceId'
    )
    s3_link = models.URLField(_("S3 Link"), db_column='s3Link')
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='processing'
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        db_table = "bulk_uploads"
        verbose_name = _("Bulk Upload")
        verbose_name_plural = _("Bulk Uploads")

    def __str__(self):
        return f"Bulk Upload {self.upload_id} - {self.status}"