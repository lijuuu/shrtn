"""
User signals for automatic organization creation.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from core.dependencies.service_registry import service_registry

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_default_organization(sender, instance, created, **kwargs):
    """
    Automatically create a default organization when a user signs up.
    The user becomes the admin of this organization.
    """
    if created:
        try:
            # Get organization service
            org_service = service_registry.get_organization_service()
            
            # Create default organization
            org_data = {
                'name': f"{instance.get_full_name()}'s Organization",
                'owner_id': instance.id
            }
            
            organization = org_service.create(org_data)
            
            logger.info("Created default organization '%s' for user %s", 
                       organization.name, instance.email)
            
        except Exception as e:
            logger.error("Failed to create default organization for user %s: %s", 
                        instance.email, e)
            # Don't raise here to avoid breaking user creation
