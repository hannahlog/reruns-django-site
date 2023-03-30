from django.db import transaction
from django.core.files.base import ContentFile
from django.utils import timezone
from celery import shared_task
from rssreruns.feedmodifier import FeedModifier as FM
from .models import RerunsFeed

@shared_task()
def update_feed(feed_pk, num_entries):
    reruns_feed = RerunsFeed.objects.get(pk=feed_pk)
    with reruns_feed.source_file.open() as f:
        fm = FM.from_string(f.read())
    with transaction.atomic():
        if fm.num_remaining() == 0:
            reruns_feed.active = False
        else:
            fm.rebroadcast(num_entries)
        reruns_feed.source_file.save(
            name="",
            content=ContentFile(fm.write(path=None, pretty_print=False).encode("utf-8")),
            save=False
        )
        reruns_feed.last_task_run = timezone.now()
        reruns_feed.task_run_count += 1
        reruns_feed.save(
            update_fields={
                "active",
                "contents",
                "source_file",
                "task_run_count",
                "last_task_run",
                "next_task_run"
            }
        )
