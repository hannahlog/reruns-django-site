# from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models.signals import post_save
from django.db.models import DEFERRED
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django_celery_beat.models import IntervalSchedule, PeriodicTask
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

# The Positive[Big]Integer fields actually allow 0 (despite their name)
strictly_positive = MinValueValidator(
    limit_value=1, message="Please enter a positive integer (not zero)."
)

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

    interval = models.PositiveIntegerField(blank=False, validators=[strictly_positive])
    entries_per_update = models.PositiveIntegerField(blank=False, validators=[strictly_positive])

    last_edited = models.DateTimeField(auto_now=True)

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

    task_run_count = models.PositiveBigIntegerField(default=0)
    start_time = models.DateTimeField(
        default=timezone.now,
        #blank=True,
        null=False,
        help_text=\
            "Scheduled datetime for the feed to first be updated " \
            "(YYYY-MM-DD HH:MM, with HH in 24-hour time)"
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

    def save(self, *args, update_fields=None, **kwargs):
        # TODO: REORGANIZE / REFACTOR, move validation aspects into validation
        # (while remembering that not all calls to save() are through ModelForms,
        # the update_feed tasks also update RerunsFeeds)
        print("Update_fields:")
        print(update_fields)
        update_fields = self._update_fields_safe(update_fields)
        print(update_fields)

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

            interval_delta = datetime.timedelta(
                **{self.interval_unit.lower(): self.interval}
            )

            defaults = {
                "interval": schedule,
                "task": "reruns.tasks.update_feed",
                "kwargs": {
                    "feed_pk": self.pk,
                    "num_entries": self.entries_per_update,
                }
            }

            start_time_changed = self._actually_changed("start_time", update_fields)
            interval_changed = self._actually_changed("interval_unit", update_fields) \
                            or self._actually_changed("interval", update_fields)

            if not start_time_changed:
                # Otherwise, load the existing value
                # (for calculating next_task_run if applicable)
                self.start_time = self._loaded_values["start_time"]

            if start_time_changed or interval_changed:
                # If either has been changed, the PeriodicTask's schedule will have
                # to be updated. Same if the expected next task has been missed.

                # A newly-supplied starting datetime cannot be in the past
                # (Offset is used just in case saving to the database is
                # unusually slow.)
                self.start_time = max(self.start_time, self.now_plus_offset())

                defaults["start_time"] = self.start_time

                # The start_time will have issues without setting this. See:
                # https://stackoverflow.com/a/57505333
                # https://github.com/celery/django-celery-beat/issues/259
                defaults["last_run_at"] = self.start_time - interval_delta

            task, new_task_created = PeriodicTask.objects.update_or_create(
                defaults=defaults,
                name=f"{self.owner.username} | {self.source_url} | {self.created}"
            )

            self.task = task
            self.task.enabled = self.active

            if self.active:
                # Estimate the next upcoming run of the PeriodicTask
                if self.start_time and (self.start_time > timezone.now()):
                     self.next_task_run = self.start_time
                else:
                    self.next_task_run = (self.task.last_run_at or self.last_task_run or self.start_time) + interval_delta
            else:
                # If feed updates are disabled, there's no upcoming task run
                self.next_task_run = None

            self.last_edited = timezone.now()
            return super().save(*args, update_fields=update_fields, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete associated task when RerunsFeed is deleted."""
        with transaction.atomic():
            self.task.delete()
            return super(self.__class__, self).delete(*args, **kwargs)

    def _actually_changed(self, name, update_fields):
        """Check whether a field's value has changed since being loaded from the database."""
        return (not hasattr(self, "_loaded_values")) or (
            (update_fields is None or name in update_fields)
            and self.__getattribute__(name)
            and self.__getattribute__(name) != self._loaded_values[name]
        )

    def _update_fields_safe(self, update_fields):
        if update_fields is not None:
            # For some fields, other fields should also be able to be updated.
            #
            # (Ideally, the code calling save() will list all of the fields to be
            # updated anyway. However, if save is called with update_fields containing
            # e.g. title_prefix but not contents, this ensures that contents is able
            # to be updated.)
            update_fields = set(update_fields)
            update_fields.discard("id")
            update_fields.add("last_edited")
            # if self.next_task_run < timezone.now():
            #    update_fields.add("next_task_run")

            field_cliques = (
                {
                    "task", "start_time", "interval", "interval_unit", "next_task_run"
                },
                {
                    "contents",
                    "title_prefix", "title_suffix", "title",
                    "entry_title_prefix", "entry_title_suffix",
                    "run_forever", "entry_order",
                }
            )
            field_dependencies = {
                "entries_per_update": {"task"},
                "active": {"next_task_run"},
                "last_task_run": {"task_run_count", "active", "next_task_run"}
            }

            for clique in field_cliques:
                # Update the entire clique if any of its elements are being updated
                if update_fields & clique:
                    update_fields |= clique
            for field, dependencies in field_dependencies.items():
                # Update its dependencies if a field is being updated
                if field in update_fields:
                    update_fields |= dependencies

        return update_fields

    @classmethod
    def now_plus_offset(cls):
        """The current datetime, but with a little wiggle room."""
        return cls._datetime_minute_ceiling(
            timezone.now() + datetime.timedelta(minutes=2)
        )

    @staticmethod
    def _datetime_minute_ceiling(dt):
        """Round a given datetime to the nearest minute >= the original datetime."""
        minute_floor = dt.replace(second=0, microsecond=0)
        return dt if dt == minute_floor else minute_floor + datetime.timedelta(minutes=1)

    @classmethod
    def from_db(cls, db, field_names, values):
        # Recipe taken from the Django docs here:
        # https://docs.djangoproject.com/en/4.1/ref/models/instances/#customizing-model-loading
        instance = super().from_db(db, field_names, values)

        # customization to store the original field values on the instance
        instance._loaded_values = dict(
            zip(field_names, (value for value in values if value is not DEFERRED))
        )
        return instance

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