from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth.models import User
from timezone_field import TimeZoneField


class CustomUser(AbstractUser):
    # Setting the user OneToOneField as the primary key did Not work as expected. Blegh.
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = TimeZoneField(default="US/Eastern")

    def get_absolute_url(self):
        return reverse('accounts:detail', kwargs={"pk": self.pk})