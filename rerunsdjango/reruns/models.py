from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.

class RerunsFeed(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # text = models.TextField()
    creation_date = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    source_url = models.URLField(max_length=200)
    source_title = models.CharField(max_length=200)



# class Choice(models.Model):
#    question = models.ForeignKey(Question, on_delete=models.CASCADE)
#    choice_text = models.CharField(max_length=200)
#    votes = models.IntegerField(default=0)