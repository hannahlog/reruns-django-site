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
import json

MINUTES = "minutes"
HOURS = "hours"
DAYS = "days"

RANDOM = "random"
CHRONOLOGICAL = "chron"

RSS = "rss"
ATOM = "atom"

class RerunsFeed(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created"
    )

    # Exactly one of these is required to create a model instance
    source_url = models.URLField(max_length=200, blank=True, null=False)
    source_file = models.FileField(blank=True, null=True)

    contents = models.TextField()
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=200)

    title_prefix = models.CharField(default="",
        max_length=200,
        blank=True,
        null=False,
        help_text="Leave blank for no prefix."
    )
    title_suffix = models.CharField(default="",
        max_length=200,
        blank=True,
        null=False,
        help_text="Leave blank for no suffix."
    )

    entry_title_help_text = \
        "Entry title prefixes and suffixes are used as format strings for " \
        "the entry's <i>original</i> publication date, via <code>strftime</code>."
    entry_title_prefix = models.CharField(
        default="",
        max_length=200,
        blank=True,
        null=False,
        help_text=entry_title_help_text + " Leave blank for no prefix."
    )
    entry_title_suffix = models.CharField(
        default="",
        max_length=200,
        blank=True,
        null=False,
        help_text=entry_title_help_text + " Leave blank for no suffix."
    )

    interval = models.IntegerField(blank=False)
    entries_per_update = models.IntegerField(blank=False)

    last_edited = models.DateTimeField(default=timezone.now)

    last_task_run = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Last Updated"
    )

    next_task_run = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Next Update (Estimate)"
    )

    task_run_count = models.BigIntegerField(default=0)
    start_time = models.DateTimeField(
        default=timezone.now,
        help_text=\
            "Scheduled datetime for the feed to first be updated " \
            "(YYYY-MM-DD HH:MM, with HH in 24-hour time)"
    )
    use_timezone = TimeZoneField(
        # choices_display="WITH_GMT_OFFSET",
        blank=True,
        help_text=
            "(Timezone for the given start time. "\
            "Leave blank to use your account's timezone setting.)"
    )

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

    task = models.OneToOneField(
        PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL
    )

    FEED_TYPE_CHOICES = [
        (RSS, "RSS"),
        (ATOM, "Atom"),
    ]
    feed_type = models.CharField(
        max_length=4,
        choices=FEED_TYPE_CHOICES,
        blank=False,
    )

    def get_absolute_url(self):
        return reverse('reruns:detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        # TODO: REORGANIZE / REFACTOR, move validation aspects into validation
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
                # Initialize the feed, either from URL or the provided file
                if self.source_url:
                    fm = FM.from_url(self.source_url, **fm_kwargs)
                elif self.source_file:
                    file_text = self.source_file.open().read()
                    fm = FM.from_string(file_text, **fm_kwargs)
                    self.source_file = None
                    self.source_url = fm.source_url()
                self.feed_type = fm.feed_type().lower()
            else:
                # Load the already-existing feed contents
                fm = FM.from_string(self.contents, **fm_kwargs)

            fm["order"] = (
                "chronological"
                if self.entry_order == CHRONOLOGICAL
                else "random"
            )
            self.contents = fm.write(path=None, pretty_print=False)
            self.title = fm["title"]

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

            # Starting datetime cannot be in the past
            # (Offset is used just in case saving to the database is unusually slow.)
            self.start_time = max(self.start_time, self.now_plus_offset())

            interval_delta = datetime.timedelta(
                **{self.interval_unit.lower(): self.interval}
            )

            task, new_task_created = PeriodicTask.objects.update_or_create(
                defaults={
                    "interval": schedule,
                    "task": "reruns.tasks.update_feed",
                    "start_time": self.start_time,
                    # The start_time will have issues without setting this. See:
                    # https://stackoverflow.com/a/57505333
                    # https://github.com/celery/django-celery-beat/issues/259
                    "last_run_at": self.start_time - interval_delta,
                    "kwargs": {
                        "feed_pk": self.pk,
                        "num_entries": self.entries_per_update,
                    },
                },
                name=f"{self.owner.username} | {self.source_url} | {self.created}",
            )

            self.task = task
            self.task.enabled = self.active

            if self.active:
                # Estimate the next upcoming run of the PeriodicTask
                if self.start_time > timezone.now():
                     self.next_task_run = self.start_time
                else:
                    seconds_remaining = schedule.remaining_estimate(self.task.last_run_at)
                    self.next_task_run = self.timezone.now() + seconds_remaining
            else:
                # If feed updates are disabled, there's no upcoming task run
                self.next_task_run = None

            self.last_edited = timezone.now()
            return super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        """Delete associated task when RerunsFeed is deleted."""
        with transaction.atomic():
            self.task.delete()
            return super(self.__class__, self).delete(*args, **kwargs)

    def next_task_run_estimate(self):
        schedule = self.task.schedule
        seconds_remaining = schedule.remaining_estimate(self.task.last_run_at)
        return timezone.now() + seconds_remaining

    def now_plus_offset(self):
        """The current datetime, but with a little wiggle room."""
        return timezone.now() + datetime.timedelta(minutes=2)

@receiver(post_save, sender=RerunsFeed)
def update_task_kwargs(sender, instance, created, **kwargs):
    # If this is a newly-created RerunsFeed, its pk will be None when the
    # PeriodicTask is first created in save(), so the task's keyword arguments will
    # incorrectly have feed_pk=None.
    #
    # After save(), the RerunsFeed's pk exists, so the task kwargs can be fixed.
    instance.task.kwargs = json.dumps({
        "feed_pk": instance.pk,
        "num_entries": instance.entries_per_update
    })
    instance.task.save()