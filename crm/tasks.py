from elk.celery import app as celery


@celery.task
def notify_about_last_lesson():
    pass
