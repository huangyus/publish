import os
import shutil
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import *
from api.tasks import PullRepo


@receiver(post_save, sender=Modules, dispatch_uid="modules_post_save")
def createRepo(sender, instance, created, **kwargs):
    if created:
        PullRepo.delay(instance.id, refresh=False)


@receiver(post_delete, sender=Modules, dispatch_uid="modules_post_delete")
def deleteRepo(sender, instance, **kwargs):
    repo_dir = os.path.join(instance.repo_work.strip(), instance.env, instance.name)
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
