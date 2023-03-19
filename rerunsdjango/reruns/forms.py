from django import forms
from django.utils import timezone
from .models import RerunsFeed
from django.core.exceptions import ValidationError
import datetime
from django.forms.utils import to_current_timezone


class WorkingSplitDateTimeField(forms.SplitDateTimeField):
    def decompress(self, value):
        return ' '.join(value)

class WorkingSplitDateTimeWidget(forms.widgets.SplitDateTimeWidget):
    def decompress(self, value):
        return value

class RerunsFeedAddForm(forms.ModelForm):

    class Meta:
        model = RerunsFeed
        fields = [
                "source_url",
                "source_file",
                "interval",
                "interval_unit",
                "entries_per_update",
                "start_time",
                "use_timezone",
                "title_prefix",
                "title_suffix",
                "entry_title_prefix",
                "entry_title_suffix",
                "entry_order",
                "run_forever",
                "active",
            ]
        widgets = {
            'start_time': forms.widgets.DateTimeInput(format="%Y-%m-%d %H:%M")
        }

        # start_date = WorkingSplitDateTimeField(widget=WorkingSplitDateTimeWidget)
        # widgets = {
        #     'start_time': WorkingSplitDateTimeWidget(
        #             date_format="%Y-%m-%d",
        #             time_format="%H:%M",
        #             date_attrs={
        #                 'class': 'form-control',
        #                'placeholder': timezone.now(),
        #                'type': 'date'
        #             },
        #             time_attrs={
        #                 'class': 'form-control',
        #                'placeholder': timezone.now(),
        #                'type': 'time'
        #             }
        #     )
        # }
        #widgets = {"start_time": forms.widgets.DateTimeInput}

    #def post(self, request, *args, **kwargs):
    #    print(request)
    #    super().post(request, *args, **kwargs)

    #def _clean_fields(self):
    #    super()._clean_fields()

    def clean(self):
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
        super().clean()
        print("HEWWWWWWWWWOOOOOO")
        # Ensure exactly one of source_url or source_file is provided
        # (source_url XOR source_file)
        source_url = self.cleaned_data.get("source_url")
        source_file = self.cleaned_data.get("source_file")

        print(source_url)
        print(source_file)

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

    class Meta:
        model = RerunsFeed
        fields = [
            "interval",
            "interval_unit",
            "entries_per_update",
            "start_time",
            "use_timezone",
            "title_prefix",
            "title_suffix",
            "entry_title_prefix",
            "entry_title_suffix",
            "entry_order",
            "run_forever",
            "active",
        ]
        widgets = {
            'start_time': forms.widgets.DateTimeInput(
                                format="%Y-%m-%d %H:%M"
                            )
        }

    def __init__(self, *args, **kwargs):
        super(RerunsFeedUpdateForm, self).__init__(*args, **kwargs)
        print(self.fields["start_time"].initial())
        print(self.initial["start_time"])
        print(self.fields["start_time"])
        #self.fields["start_time"] = self.initial["start_time"]

        print(self.fields["start_time"].initial())
        print(self.initial["start_time"])
        self.fields["start_time"].required = False
        self.initial["start_time"] = None
        #self.fields["use_timezone"].required = False
        #self.initial["use_timezone"] = None

    def save(self, commit=True):
        print("SCREAMING")
        update_fields=None
        print(self.changed_data)
        # update_fields = self.changed_data
        if "start_time" not in self.changed_data:
            print("BWAAAAAAAAAAAAAAAAAAAAA")
            update_fields = set(f.name for f in self.Meta.model._meta.get_fields()) - {"start_time"}
            print(update_fields)
        instance = super(RerunsFeedUpdateForm, self).save(commit=False)
        print("pls work")
        instance.save(update_fields=update_fields)
        return instance