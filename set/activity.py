# set/activity.py

from django.utils import timezone
from .models import SoftwareActivity, Project


def log_activity(message, event_type="project", user=None, project: Project | None = None):
    """
    Simple helper for creating activity logs in SET module.
    """
    SoftwareActivity.objects.create(
        message=message,
        type=event_type,
        user=user,
    )
