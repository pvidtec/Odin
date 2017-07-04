from odin.common.faker import faker

from test_plus import TestCase

from odin.users.models import BaseUser

from odin.users.factories import BaseUserFactory

import os


class AuthorizationTests(TestCase):
    def setUp(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'

    def tearDown(self):
        del os.environ['RECAPTCHA_TESTING']

    def test_user_registration_with_recaptcha_passed(self):
        user_count = BaseUser.objects.count()
        url = self.reverse('account_signup')
        password = faker.password()
        data = {
            'email': faker.email(),
            'password1': password,
            'g-recaptcha-response': 'PASSED'
        }
        response = self.post(url_name=url, data=data, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user_count + 1, BaseUser.objects.count())

    def test_user_registration_with_recaptcha_not_passed(self):
        user_count = BaseUser.objects.count()
        url = self.reverse('account_signup')
        password = faker.password()
        data = {
            'email': faker.email(),
            'password1': password,
        }
        response = self.post(url_name=url, data=data, follow=False)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user_count, BaseUser.objects.count())

    def test_user_registration_for_already_logged_in_user(self):
        test_password = faker.password()
        user = BaseUserFactory(password=test_password)
        user.is_active = True
        user.save()
        user_count = BaseUser.objects.count()
        with self.login(email=user.email, password=test_password):
            url = self.reverse('account_signup')
            response = self.get(url_name=url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(user_count, BaseUser.objects.count())
