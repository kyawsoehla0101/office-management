from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Task
from .activity import log_activity

@receiver(post_save, sender=Task)
def task_saved(sender, instance, created, **kwargs):
    project = instance.project

    if created:
        log_activity(
            f"🆕 Task '{instance.title}' created in project '{project.title}'",
            "task",
            None
        )
    else:
        if instance.status == "DONE":
            log_activity(
                f"✔ Task '{instance.title}' completed in project '{project.title}'",
                "task",
                None
            )

@receiver(post_delete, sender=Task)
def task_deleted(sender, instance, **kwargs):
    project = instance.project
    log_activity(
        f"❌ Task '{instance.title}' deleted from project '{project.title}'",
        "task",
        None
    )
