# Generated by Django 4.1 on 2023-03-15 19:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reruns", "0006_rerunsfeed_source_file_alter_rerunsfeed_source_url_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="rerunsfeed",
            old_name="creation_date",
            new_name="created",
        ),
    ]
