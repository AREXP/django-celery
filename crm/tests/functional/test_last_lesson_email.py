from unittest.mock import patch

from django.core import mail
from freezegun import freeze_time

from crm.tasks import notify_lost_customers
from elk.utils.testing import TestCase, create_customer


class LastLessonEmailTest(TestCase):
    @patch('market.signals.Owl')
    def test_send_email(self, Owl):
        customer = create_customer()
        with freeze_time('2021-04-20 15:00'):
            customer.set_last_lesson_date()

        # move one week and hour forward
        with freeze_time('2021-04-27 16:00'):
            notify_lost_customers()

        self.assertEqual(len(mail.outbox), 1)

        out_email = mail.outbox[0]
        self.assertEqual(customer.email, out_email.to[0])
        self.assertEqual(out_email.template_name, 'mail/last_lesson_a_long_ago.html')

    def test_reset_last_lesson_after_email(self):
        customer = create_customer()
        later_customer = create_customer()
        no_lesson_customer = create_customer()

        with freeze_time('2021-04-20 15:00'):
            customer.set_last_lesson_date()

        # a few days later
        with freeze_time('2021-04-22 15:00'):
            later_customer.set_last_lesson_date()

        # move one week and hour forward
        with freeze_time('2021-04-27 16:00'):
            notify_lost_customers()

        customer.refresh_from_db()
        self.assertIsNone(customer.last_lesson_date)

        later_customer.refresh_from_db()
        self.assertIsNotNone(later_customer.last_lesson_date)

        no_lesson_customer.refresh_from_db()
        self.assertIsNone(no_lesson_customer.last_lesson_date)
