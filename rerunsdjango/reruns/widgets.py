from django import forms
from django.utils import timezone
from .models import RerunsFeed
from django.core.exceptions import ValidationError
import datetime
from django.forms.utils import to_current_timezone
from timezone_field import TimeZoneFormField, TimeZoneField
from timezone_field import choices


class SplitDateTimeTimezoneWidget(forms.MultiWidget):
    supports_microseconds = False
    template_name = "django/forms/widgets/splitdatetime.html"

    def __init__(
        self,
        attrs=None,
        date_format=None,
        time_format=None,
        date_attrs=None,
        time_attrs=None,
        timezone_attrs=None,
    ):
        widgets = (
            forms.DateInput(
                attrs=attrs if date_attrs is None else date_attrs,
                format=date_format,
            ),
            forms.TimeInput(
                attrs=attrs if time_attrs is None else time_attrs,
                format=time_format,
            ),
            TimeZoneFormField.widget(
                attrs=attrs if timezone_attrs is None else timezone_attrs,
                choices=list(choices.standard(TimeZoneField.default_zoneinfo_tzs)),
            )
        )
        super().__init__(widgets)

    def decompress(self, value):
        if value:
            value = value.astimezone(tz=timezone.get_current_timezone())
            return [value.date(), value.time(), value.tzinfo.key]
        return [None, None, None]
