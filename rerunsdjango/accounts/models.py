from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from timezone_field import TimeZoneField


class CustomUser(AbstractUser):
    # Same as the default User, but now with a timezone setting!
    # (And other fields can easily be added without having a separate UserSettings
    # model with a User as the OneToOneField etc.)
    timezone = TimeZoneField(default="US/Eastern")

    def get_absolute_url(self):
        return reverse('accounts:detail', kwargs={"pk": self.pk})