from datetime import datetime, timedelta

from crm.models import Customer
from crm.signals import lost_customer_notification
from elk import settings
from elk.celery import app as celery


@celery.task
def notify_lost_customers():
    border_date = datetime.now() - timedelta(days=settings.NOTIFY_LOST_CUSTOMERS_DAYS)
    for customer in Customer.objects.filter(last_lesson_date__lte=border_date):
        lost_customer_notification.send(
            sender=notify_lost_customers, instance=customer,
        )
        customer.erase_last_lesson_date()
        customer.save()
