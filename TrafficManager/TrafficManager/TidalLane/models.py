from django.db import models

# Create your models here.
class tidallane(models.Model):
    objects = models.Manager()
    time = models.DateTimeField()
    ori_volume = models.IntegerField()
    ori_wait = models.IntegerField()
    tid_volume = models.IntegerField()
    tid_wait = models.IntegerField()