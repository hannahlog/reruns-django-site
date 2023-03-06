from django.db import transaction
from django.utils import timezone
from celery import shared_task
from rssreruns.feedmodifier import FeedModifier as FM
from .models import RerunsFeed

i = 0

@shared_task()
def hello_task():
    print(f"Hello world! Iteration: {i}")

@shared_task()
def update_feed(feed_pk, num_entries):
    reruns_feed = RerunsFeed.get(pk=feed_pk)
    fm = FM.from_string(reruns_feed.contents)
    with transaction.atomic():
        if fm.num_remaining() == 0:
            reruns_feed.is_active = False
        else:
            fm.rebroadcast(num_entries)
        reruns_feed.contents = fm.write(path=None)
        reruns_feed.last_updated = timezone.now()
        reruns_feed.task_run_count += 1
        reruns_feed.save()

