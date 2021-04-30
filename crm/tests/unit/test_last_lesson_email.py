from unittest.mock import patch

from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer

from crm.tasks import notify_about_last_lesson


class LastLessonEmailTest(TestCase):

    @patch('market.signals.Owl')
    def test_send_email(self, Owl):
        pass

    @patch('market.signals.Owl')
    def test_reset_last_lesson_after_email(self, Owl):
        customer = create_customer()
        with freeze_time('2021-04-20 15:00'):
            customer.set_last_lesson_date()

        # move one week and hour forward
        with freeze_time('2021-04-27 16:00'):
            notify_about_last_lesson()

        self.assertIsNone(customer.last_subscription_lesson_date)
