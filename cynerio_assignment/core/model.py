from django.contrib.auth.models import AbstractUser
from django.db import models


class CynerioUser(AbstractUser):
    name = models.CharField(max_length=100, default='default_user')


class CynerioTask(models.Model):
    name = models.CharField(max_length=100, default='default_task')
    is_checkin = models.BooleanField(default=False)
    started = models.DateTimeField(blank=True, null=True)
