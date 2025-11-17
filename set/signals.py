from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Project, Task

@receiver([post_save, post_delete], sender=Task)
def update_project_progress(sender, instance, **kwargs):
    project = instance.project
    total = project.tasks.count()
    if total == 0:
        project.progress = 0
    else:
        completed = project.tasks.filter(status="DONE").count()
        project.progress = int((completed / total) * 100)
    project.save()
