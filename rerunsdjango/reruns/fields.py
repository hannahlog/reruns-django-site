from django import forms
from django.utils import timezone
from .models import RerunsFeed
from django.core.exceptions import ValidationError
import datetime
from django.forms.utils import to_current_timezone
from timezone_field import TimeZoneFormField, TimeZoneField
from timezone_field import choices

from .widgets import SplitDateTimeTimezoneWidget


class SplitDateTimeTimezoneField(forms.MultiValueField):

    widget = SplitDateTimeTimezoneWidget
    # hidden_widget = SplitHiddenDateTimeWidget
    default_error_messages = {
        "invalid_date": ("Enter a valid date."),
        "invalid_time": ("Enter a valid time."),
        "invalid_timezone": ("Enter a valid timezone."),
    }

    def __init__(self, *, input_date_formats=None, input_time_formats=None, **kwargs):
        errors = self.default_error_messages.copy()
        if "error_messages" in kwargs:
            errors.update(kwargs["error_messages"])
        localize = kwargs.get("localize", False)
        fields = (
            forms.DateField(
                input_formats=input_date_formats,
                error_messages={"invalid": errors["invalid_date"]},
                localize=localize,
            ),
            forms.TimeField(
                input_formats=input_time_formats,
                error_messages={"invalid": errors["invalid_time"]},
                localize=localize,
            ),
            TimeZoneFormField(required=True),
        )
        super().__init__(fields=fields, require_all_fields=True, **kwargs)

    def compress(self, data_list):
        """
        Return a single value for the given list of values. The values can be
        assumed to be valid.
        For example, if this MultiValueField was instantiated with
        fields=(DateField(), TimeField()), this might return a datetime
        object created by combining the date and time in data_list.
        """
        print(data_list)
        print(datetime.datetime.combine(
            date=data_list[0], time=data_list[1], tzinfo=data_list[2]
        ))
        return datetime.datetime.combine(
            date=data_list[0], time=data_list[1], tzinfo=data_list[2]
        )
