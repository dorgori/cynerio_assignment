from django.contrib.auth.models import User
from django.db import models


# class CynerioUser(AbstractUser):
#     name = models.CharField(max_length=100, default='default_user')


class CynerioTask(models.Model):
    name = models.CharField(max_length=100, default='default_task')
    is_checkin = models.BooleanField(default=False)


class UserCynerioTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(CynerioTask, on_delete=models.CASCADE)
    accumulated_time = models.TimeField()
