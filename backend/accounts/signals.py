"""Accounts app signals."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Initialize user preferences on creation."""
    if created:
        instance.preferences = {
            'theme': 'dark',
            'font_size': 14,
            'auto_save': True,
        }
        instance.save()
