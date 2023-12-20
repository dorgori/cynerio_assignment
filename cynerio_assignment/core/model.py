from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class CynerioTask(models.Model):
    name = models.CharField(max_length=100, default='default_task')
    is_checkin = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        try:
            # Create CynerioTask
            if not self.id:
                super(CynerioTask, self).save(*args, **kwargs)
            # Update CynerioTask
            else:
                super(CynerioTask, self).save()
                user_id = kwargs.get('user_id')
                obj, created = UserCynerioTask.objects.get_or_create(task=self, user_id=user_id)
                # Update case
                if not created:
                    if self.is_checkin:
                        # In case setting task as active, set the clock
                        obj.last_update = datetime.now()
                        obj.save()
                    else:
                        # In case setting task as inactive, calc minutes_spend
                        obj.minutes_spend = obj.minutes_spend + int((datetime.now() - obj.last_update).total_seconds() // 60)
                        obj.last_update = datetime.now()
                        obj.save()
                else:
                    obj.last_update = datetime.now()
                    obj.save()

        except Exception as e:
            raise e


class UserCynerioTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(CynerioTask, on_delete=models.CASCADE)
    last_update = models.DateTimeField(blank=True, null=True)
    minutes_spend = models.IntegerField(default=0)

    def get_time_spent(self):
        total_minutes = self.minutes_spend if not self.task.is_checkin else (
                self.minutes_spend + int((datetime.now() - self.last_update).total_seconds() // 60))
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f'{hours} hours {minutes} minutes'
