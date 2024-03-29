# Generated by Django 4.1 on 2023-03-13 18:02

from django.db import migrations, models
import django.utils.timezone
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ("reruns", "0003_rename_last_updated_rerunsfeed_last_edited_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="rerunsfeed",
            name="next_task_run",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Next Update (Estimate)"
            ),
        ),
        migrations.AlterField(
            model_name="rerunsfeed",
            name="creation_date",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Created"
            ),
        ),
        migrations.AlterField(
            model_name="rerunsfeed",
            name="entry_title_prefix",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Entry title prefixes and suffixes are used as format strings for the entry's <i>original</i> publication date, via <code>strftime</code>. Leave blank for no prefix.",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="rerunsfeed",
            name="entry_title_suffix",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Entry title prefixes and suffixes are used as format strings for the entry's <i>original</i> publication date, via <code>strftime</code>. Leave blank for no suffix.",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="rerunsfeed",
            name="last_task_run",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Last Updated"
            ),
        ),
        migrations.AlterField(
            model_name="rerunsfeed",
            name="start_time",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text="Scheduled datetime for the feed to first be updated (YYYY-MM-DD HH:MM:SS)",
            ),
        ),
        migrations.AlterField(
            model_name="rerunsfeed",
            name="title_prefix",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Leave blank for no prefix.",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="rerunsfeed",
            name="title_suffix",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Leave blank for no suffix.",
                max_length=200,
            ),
        ),
        migrations.AlterField(
            model_name="rerunsfeed",
            name="use_timezone",
            field=timezone_field.fields.TimeZoneField(
                blank=True,
                choices_display="WITH_GMT_OFFSET",
                help_text="(Timezone for the given start time. Leave blank to use your account's timezone setting.)",
            ),
        ),
    ]
