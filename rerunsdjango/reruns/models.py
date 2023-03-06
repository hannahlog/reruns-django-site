# from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from timezone_field import TimeZoneField
from rssreruns.feedmodifier import FeedModifier as FM
import datetime

MINUTES = "minutes"
HOURS = "hours"
DAYS = "days"

RANDOM = "random"
CHRONOLOGICAL = "chron"

class RerunsFeed(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(default=timezone.now)
    task_run_count = models.BigIntegerField(default=0)

    # last_updated = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    source_url = models.URLField(max_length=200)
    source_title = models.CharField(max_length=200)

    contents = models.TextField()

    interval = models.IntegerField(blank=False)
    entries_per_update = models.IntegerField(blank=False)

    title_prefix = models.CharField(max_length=200, blank=True, null=True)
    title_suffix = models.CharField(max_length=200, blank=True, null=True)
    entry_title_prefix = models.CharField(max_length=200, blank=True, null=True)
    entry_title_suffix = models.CharField(max_length=200, blank=True, null=True)

    ENTRY_ORDER_CHOICES = [
        (RANDOM, "Random"),
        (CHRONOLOGICAL, "Chronological"),
    ]

    entry_order = models.CharField(
        max_length=6,
        choices=ENTRY_ORDER_CHOICES,
        default=RANDOM,
        blank=False,
    )

    INTERVAL_UNIT_CHOICES = [
        (MINUTES, "Minutes"),
        (HOURS, "Hours"),
        (DAYS, "Days")
    ]

    interval_unit = models.CharField(
        max_length=7,
        choices=INTERVAL_UNIT_CHOICES,
        default=DAYS,
        blank=False,
    )

    run_forever = models.BooleanField(default=True)

    def now_plus_offset():
        return timezone.now() + datetime.timedelta(minutes=2)
    start_time = models.DateTimeField(default=now_plus_offset)

    use_timezone = TimeZoneField(blank=True)

    task = models.OneToOneField(
        PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL
    )

    def get_absolute_url(self):
        return reverse('reruns:detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            title_kwargs = {
                "prefix": self.title_prefix,
                "suffix": self.title_suffix,
            }
            entry_title_kwargs = {
                "prefix": self.entry_title_prefix,
                "suffix": self.entry_title_suffix,
            }
            fm_kwargs = {
                "run_forever": self.run_forever,
                "title_kwargs": title_kwargs,
                "entry_title_kwargs": entry_title_kwargs
            }
            if not self.contents:
                fm = FM.from_url(self.source_url, **fm_kwargs)
            else:
                fm = FM.from_string(self.contents, **fm_kwargs)

            fm.order = "chronological" if self.entry_order == CHRONOLOGICAL else "random"
            self.contents = fm.write(path=None)

            schedule, new_schedule_created = IntervalSchedule.objects.get_or_create(
                every=self.interval,
                # e.g. IntervalSchedule.DAYS
                period=getattr(IntervalSchedule, self.interval_unit.upper()),
            )

            if not self.use_timezone:
                self.use_timezone = self.owner.timezone

            # Interpret `start_time` as being in specified timezone, *not* the server's
            # default timezone:
            if self.start_time.tzinfo != self.use_timezone:
                # Convert the aware datetime to a naive datetime
                self.start_time.replace(tzinfo=None)
                # ...and back to aware, but with the user-specified timezone
                self.start_time.replace(tzinfo=self.use_timezone)

            task, new_task_created = PeriodicTask.objects.update_or_create(
                defaults={
                    "interval": schedule,
                    "task": "reruns.tasks.update_feed",
                    "start_time": self.start_time,
                    # The Start_time will have issues without setting this. See:
                    # https://stackoverflow.com/a/57505333
                    # https://github.com/celery/django-celery-beat/issues/259
                    "last_run_at": self.start_time - datetime.timedelta(**{self.interval_unit.lower(): self.interval}),
                    "kwargs": {
                        "feed_pk": self.pk,
                        "num_entries": self.entries_per_update,
                    },
                },
                name=f"{self.owner.username} | {self.source_url} | {self.creation_date}",
            )

            self.task = task
            return super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        """Delete associated task when RerunsFeed is deleted."""
        self.task.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def get_fields(self):
        """Kludge to allow easy listing of all (field, value)'s in a DetailView."""

        def datetime_human_format(dt):
            """Format a datetime using the specified timezone."""
            return dt.astimezone(self.use_timezone).strftime("%B %d, %Y, %H:%M %p %Z")

        # Consider rewriting, especially if literally any processing needs
        # to be done
        return [
            (
                field.verbose_name,
                field.value_from_object(self)
                if not isinstance(field.value_from_object(self), datetime.datetime)
                else datetime_human_format(field.value_from_object(self))
            )
            for field in self.__class__._meta.fields
        ]

    def next_task_run_estimate(self):
        schedule = self.task.schedule
        seconds_remaining = schedule.remaining_estimate(self.task.last_run_at)
        return timezone.now() + seconds_remaining

@receiver(post_save, sender=RerunsFeed)
def update_task_kwargs(sender, instance, created, **kwargs):
    # If this is a newly-created RerunsFeed, its pk will be None when the
    # PeriodicTask is first created in save(), so the task's keyword arguments will
    # incorrectly have feed_pk=None.
    #
    # After save(), the RerunsFeed's pk exists, so the task kwargs can be fixed.
    instance.task.kwargs = {
        "feed_pk": instance.pk,
        "num_entries": instance.entries_per_update,
    }
    instance.task.save()