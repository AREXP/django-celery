from datetime import datetime, timedelta

from elk import settings
from elk.celery import app as celery
from crm.models import Customer
from crm.signals import send_last_lesson_email


@celery.task
def notify_about_last_lesson():
    border_date = datetime.now() - timedelta(days=settings.LAST_LESSON_STUDENT_NOTIFY_DAYS)
    for customer in Customer.objects.filter(last_subscription_lesson_date__lte=border_date):
        notify_about_last_lesson.send(
            sender=send_last_lesson_email, instance=customer,
        )
        customer.erase_last_lesson_date()
        customer.save()
