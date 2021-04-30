from elk.utils.testing import TestCase


class LastLessonTest(TestCase):
    def test_true(self):
        self.assertTrue(True)

    def test_no_email_without_lesson(self):
        pass

    def test_no_email_with_subscription_without_lesson(self):
        pass

    def test_reset_last_lesson_after_email(self):
        pass

    def test_no_reset_after_cancelled_lesson(self):
        pass

    def test_send_email(self):
        pass

    def test_dont_set_last_lesson_without_subscription(self):
        pass

    def test_clean_last_lesson_after_subscription(self):
        pass

    def test_last_lesson_with_renew(self):
        pass

    def test_clean_last_lesson_after_finish_all_lessons(self):
        pass
