from django import forms
from django.utils import timezone
from .models import RerunsFeed
from django.core.exceptions import ValidationError
import datetime
from django.forms.utils import to_current_timezone
from timezone_field import TimeZoneFormField, TimeZoneField
from timezone_field import choices

from .widgets import SplitDateTimeTimezoneWidget
from .fields import SplitDateTimeTimezoneField

class RerunsFeedAddForm(forms.ModelForm):

    start_time = SplitDateTimeTimezoneField(widget=
        SplitDateTimeTimezoneWidget(
            date_attrs={
                'class': 'form-control',
                'type': 'date',
            },
            time_attrs={
                'class': 'form-control',
                'type': 'time',
                "time_format": "%H:%M",
            },
            time_format = "%H:%M",
        ),
    )

    class Meta:
        model = RerunsFeed
        fields = [
                "source_url",
                "source_file",
                "interval",
                "interval_unit",
                "entries_per_update",
                "start_time",
                "title_prefix",
                "title_suffix",
                "entry_title_prefix",
                "entry_title_suffix",
                "entry_order",
                "run_forever",
                "active",
            ]

    def __init__(self, *args, **kwargs):
        super(RerunsFeedAddForm, self).__init__(*args, **kwargs)
        self.fields["start_time"].initial = (
            timezone.now()
            .astimezone(tz=timezone.get_current_timezone())
            .replace(second=0, microsecond=0)
        )

    def clean(self):
        super().clean()
        # Ensure exactly one of source_url or source_file is provided
        # (source_url XOR source_file)
        source_url = self.cleaned_data.get("source_url")
        source_file = self.cleaned_data.get("source_file")

        if source_url and source_file:
            raise ValidationError(
                "Exactly one of Source Url or Source File must be provided, not both."
            )
        if not (source_url or source_file):
            raise ValidationError(
                "Either a Source Url or Source File must be provided."
            )
        if any(self.errors):
            return self.errors

class RerunsFeedUpdateForm(forms.ModelForm):

    start_time = SplitDateTimeTimezoneField(widget=
        SplitDateTimeTimezoneWidget(
            date_attrs={
                'class': 'form-control',
                'type': 'date',
            },
            time_attrs={
                'class': 'form-control',
                'type': 'time',
                "time_format": "%H:%M",
            },
            timezone_attrs={
                'class': 'form-control',
                'type': 'tzinfo',
                "require": "False",
            }
        )
    )

    class Meta:
        model = RerunsFeed
        fields = [
            "interval",
            "interval_unit",
            "entries_per_update",
            "start_time",
            "title_prefix",
            "title_suffix",
            "entry_title_prefix",
            "entry_title_suffix",
            "entry_order",
            "run_forever",
            "active",
        ]

    def save(self, commit=True):
        # TODO: Actually make use of update_fields for efficiency
        update_fields=None
        # update_fields = self.changed_data
        if "start_time" not in self.changed_data:
            update_fields = set(f.name for f in self.Meta.model._meta.get_fields()) - {"start_time"}
        instance = super(RerunsFeedUpdateForm, self).save(commit=False)
        instance.save(update_fields=update_fields)
        return instance