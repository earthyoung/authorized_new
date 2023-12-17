from django.test import TestCase
from account.models import *


# Create your tests here.
class UserTest(TestCase):
    def test_user_provider_is_in_range(self):
        user = User.objects.create(email="xnkjxnfkdsnf@gmail.com")
        self.assertIn(user.provider, User.Provider.values)

    def test_user_email_google(self):
        user = User.signup_manager.create(email="dshfksafj@gmail.com", username="111")
        self.assertEqual(user.provider, User.Provider.GOOGLE.value)

    def test_user_email_others(self):
        user = User.signup_manager.create(email="sjkafnkjsf@naver.com", username="222")
        self.assertEqual(user.provider, User.Provider.KAKAO.value)
