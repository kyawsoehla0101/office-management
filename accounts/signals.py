# accounts/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default_settings(sender, **kwargs):
    from base.models import SystemSettings
    if sender.name == 'accounts':
        SystemSettings.objects.get_or_create(id=1)
