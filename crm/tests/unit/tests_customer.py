from django.core.exceptions import ValidationError
from django.test import override_settings
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer
from lessons import models as lessons
from market.models import Class


class CustomerTestCase(TestCase):
    # fixtures = ('crm',)

    def test_user_model(self):
        """
        Customer objects with assigned django user should take user data from
        the django table.
        """
        customer = create_customer()

        customer.user.first_name = 'Fedor'
        customer.user.last_name = 'Borshev'
        customer.user.email = 'f@f213.in'
        customer.user.save()

        self.assertEqual(customer.full_name, 'Fedor Borshev')
        self.assertEqual(customer.first_name, 'Fedor')
        self.assertEqual(customer.last_name, 'Borshev')
        self.assertEqual(customer.email, 'f@f213.in')

    def test_can_cancel_classes(self):
        customer = create_customer()

        self.assertTrue(customer.can_cancel_classes())
        customer.cancellation_streak = 5
        customer.max_cancellation_count = 5
        self.assertFalse(customer.can_cancel_classes())

    def test_can_schedule_classes(self):
        customer = create_customer()

        self.assertFalse(customer.can_schedule_classes())
        c = Class(
            lesson_type=lessons.OrdinaryLesson.get_contenttype(),
            customer=customer
        )
        c.save()
        self.assertTrue(customer.can_schedule_classes())

    def test_invalid_timezone(self):
        """
        Assign an invalid timezone to the customer
        """
        c = create_customer()
        with self.assertRaises(ValidationError):
            c.timezone = 'Noga/Test'
            c.save()

    def test_profile_needs_updating_false(self):
        c = create_customer()
        c.skype = 'tstskp'
        c.save()
        self.assertFalse(c.profile_needs_updating())

    def test_profile_neeeds_updating_true(self):
        c = create_customer()
        c.skype = ''
        c.save()
        self.assertTrue(c.profile_needs_updating())

    def test_get_absolute_url(self):
        c = create_customer()

        url = c.get_absolute_url()
        self.assertIn(str(c.pk), url)
        self.assertIn('/admin/', url)

    def test_customer_profile_automaticaly_emerges_when_creating_stock_django_user(self):
        u = mixer.blend('auth.User')
        self.assertIsNotNone(u.crm)

    @freeze_time('2021-04-30 15:00')
    @override_settings(TIME_ZONE='Europe/Moscow')
    def test_set_last_lesson_date(self):
        customer = create_customer()
        customer.set_last_lesson_date()
        last_lesson = customer.last_subscription_lesson_date
        self.assertEqual(last_lesson, self.tzdatetime(2021, 4, 30, 18))

    def test_erase_last_lesson_date(self):
        customer = create_customer()
        customer.set_last_lesson_date()
        self.assertIsNotNone(customer.last_subscription_lesson_date)

        customer.erase_last_lesson_date()
        self.assertIsNone(customer.last_subscription_lesson_date)
