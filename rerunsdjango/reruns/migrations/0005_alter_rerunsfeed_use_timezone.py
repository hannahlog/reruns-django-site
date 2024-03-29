# Generated by Django 4.1 on 2023-03-13 18:16

from django.db import migrations
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ("reruns", "0004_rerunsfeed_next_task_run_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rerunsfeed",
            name="use_timezone",
            field=timezone_field.fields.TimeZoneField(
                blank=True,
                help_text="(Timezone for the given start time. Leave blank to use your account's timezone setting.)",
            ),
        ),
    ]
