from django.test import TestCase
from account.models import *
from account.exception import *


# Create your tests here.
class UserTest(TestCase):
    def test_user_provider_is_in_range(self):
        user = User.objects.create(email="xnkjxnfkdsnf@gmail.com")
        self.assertEqual(user.provider, User.Provider.COMMON.value)

    def test_user_email_google(self):
        user = User.signup_manager.create(email="dshfksafj@gmail.com", username="111")
        self.assertEqual(user.provider, User.Provider.GOOGLE.value)

    def test_user_email_others(self):
        user = User.signup_manager.create(email="sjkafnkjsf@naver.com", username="222")
        self.assertEqual(user.provider, User.Provider.KAKAO.value)


class PermissionTest(TestCase):
    def test_health_api(self):
        response = self.client.get("/account/health/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_api_without_jwt(self):
        def call_user():
            return self.client.get("/account/user/")

        # response = call_user()
        self.assertRaises(JwtNotExistException, call_user)
        # self.assertEqual(True, True)

    def test_logout_api_without_jwt(self):
        def call_api():
            return self.client.post("/account/logout/")

        # response = call_api()
        self.assertRaises(JwtNotExistException, call_api)
        # self.assertEqual(True, True)
