from .models import SoftwareActivity

def log_activity(message, activity_type="project", user=None):
    SoftwareActivity.objects.create(
        message=message,
        type=activity_type,
        user=user
    )
