from datetime import timedelta

from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import TestCase, create_customer, create_teacher
from lessons import models as lessons
from market.models import Class, Subscription
from products.models import Product1


class LastLessonTest(TestCase):
    fixtures = ('products', 'lessons')

    @classmethod
    def setUpTestData(cls):
        cls.product = Product1.objects.get(pk=1)
        cls.product.duration = timedelta(days=5)
        cls.product.save()

    def setUp(self):
        self.customer = create_customer()

    def _buy_a_lesson(self):
        c = Class(
            customer=self.customer,
            lesson_type=lessons.OrdinaryLesson.get_default().get_contenttype()
        )
        c.save()
        return c

    def _get_a_subscription(self):
        s = Subscription(
            customer=self.customer,
            product=self.product,
            buy_price=150
        )
        s.save()
        return s

    def test_no_last_lesson_without_lesson(self):
        self.assertIsNone(self.customer.last_lesson_date)

    def test_no_last_lesson_with_subscription_without_lesson(self):
        self._get_a_subscription()

        self.assertIsNone(self.customer.last_lesson_date)

    def test_set_last_lesson_after_lesson(self):
        s = self._get_a_subscription()

        entry = mixer.blend(
            'timeline.Entry',
            lesson=mixer.blend(lessons.OrdinaryLesson),
            teacher=create_teacher(),
            start=self.tzdatetime(2021, 3, 30, 12, 0)
        )
        first_class = s.classes.first()
        first_class.timeline = entry

        with freeze_time('2021-03-30 20:00'):
            self.assertTrue(first_class.has_started())
            self.assertIsNone(self.customer.last_lesson_date)

            first_class.mark_as_fully_used()

            self.customer.refresh_from_db()
            last_date = self.customer.last_lesson_date
            self.assertEqual(last_date, self.tzdatetime('UTC', 2021, 3, 30, 20))

    def test_dont_set_last_lesson_without_subscription(self):
        lesson = self._buy_a_lesson()
        lesson.mark_as_fully_used()

        self.customer.refresh_from_db()
        self.assertIsNone(self.customer.last_lesson_date)

    def test_clean_last_lesson_after_subscription(self):
        s = self._get_a_subscription()

        self.customer.set_last_lesson_date()
        self.customer.refresh_from_db()
        self.assertIsNotNone(self.customer.last_lesson_date)

        s.mark_as_fully_used()
        self.customer.refresh_from_db()
        self.assertIsNone(self.customer.last_lesson_date)

    def test_clean_last_lesson_date_after_finish_all_lessons(self):
        s = self._get_a_subscription()

        classes = [c for c in s.classes.all()]
        for klass in classes[:-1]:
            klass.mark_as_fully_used()
            self.customer.refresh_from_db()
            self.assertIsNotNone(self.customer.last_lesson_date)

        classes[-1].mark_as_fully_used()
        self.customer.refresh_from_db()
        self.assertIsNone(self.customer.last_lesson_date)

    def test_no_reset_after_cancelled_lesson(self):
        s = self._get_a_subscription()

        entry = mixer.blend(
            'timeline.Entry',
            lesson=mixer.blend(lessons.OrdinaryLesson),
            teacher=create_teacher(),
            start=self.tzdatetime(2021, 3, 31, 12, 0)
        )
        first_class = s.classes.first()
        first_class.timeline = entry

        with freeze_time('2021-03-30 20:00'):
            first_class.cancel()
            self.customer.refresh_from_db()
            self.assertIsNone(self.customer.last_lesson_date)

    def test_last_lesson_after_renew(self):
        s = self._get_a_subscription()

        self.customer.set_last_lesson_date()
        prev_last_date = self.customer.last_lesson_date
        s.renew()
        self.customer.refresh_from_db()
        self.assertEqual(prev_last_date, self.customer.last_lesson_date)

        self.customer.erase_last_lesson_date()
        none_last_date = self.customer.last_lesson_date
        s.renew()
        self.customer.refresh_from_db()
        self.assertEqual(none_last_date, self.customer.last_lesson_date)
