# Generated by Django 4.1 on 2023-02-10 02:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("django_celery_beat", "0016_alter_crontabschedule_timezone"),
    ]

    operations = [
        migrations.CreateModel(
            name="RerunsFeed",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("creation_date", models.DateTimeField(auto_now_add=True)),
                ("active", models.BooleanField(default=True)),
                ("source_url", models.URLField()),
                ("source_title", models.CharField(max_length=200)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feeds",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "task",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="django_celery_beat.periodictask",
                    ),
                ),
            ],
            options={
                "ordering": ["creation_date"],
            },
        ),
    ]