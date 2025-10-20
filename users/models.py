"""
User models for the URL shortener application.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model for the URL shortener application.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Keep username field and use email as primary identifier
    username = models.CharField(_("username"), max_length=150, unique=True, default="")
    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(_("Full Name"), max_length=255, blank=True)
    verified = models.BooleanField(_("Email Verified"), default=True) #to skip verification for now
    password_hash = models.CharField(_("Password Hash"), max_length=255, blank=True)
    google_id = models.CharField(_("Google ID"), max_length=255, blank=True, null=True, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.name or self.email

    def get_short_name(self):
        return self.name.split()[0] if self.name else self.email.split('@')[0]