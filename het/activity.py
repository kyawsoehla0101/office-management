# hardware/activity.py
from django.utils import timezone
from .models import HardwareActivity

def log_hardware(message, event_type="maintenance", user=None):
    HardwareActivity.objects.create(
        message=message,
        type=event_type,
        user=user,
        timestamp=timezone.now()
    )
