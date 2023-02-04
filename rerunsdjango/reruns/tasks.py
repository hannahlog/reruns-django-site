from celery import shared_task

i = 0

@shared_task()
def hello_task():
	print(f"Hello world! Iteration: {i}")