from django import forms
from . import RerunsFeed

class RerunsFeedAddForm(forms.ModelForm):

    class Meta:
        model = RerunsFeed
        fields = [
            "source_url",
            "interval",
            "entries_per_update",
            "start_time",
            "use_timezone",
            "title_prefix",
            "title_suffix",
            "entry_title_prefix",
            "entry_title_suffix",
            "entry_order",
            "run_forever",
        ]

