from django.contrib.auth.models import User
from django.db import models
from django_celery_beat.models import PeriodicTask

# Create your models here.

class RerunsFeed(models.Model):
    owner = models.ForeignKey('auth.User', related_name='feeds', on_delete=models.CASCADE)
    # text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    source_url = models.URLField(max_length=200)
    source_title = models.CharField(max_length=200)
    task = models.OneToOneField(
        PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ['creation_date']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

