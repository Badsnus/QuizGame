from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class StaticURLTests(TestCase):
    PROFILE_URL = reverse('users:profile')
    LOGIN_URL = reverse('users:login')
    REGISTER_URL = reverse('users:register')

    @staticmethod
    def login(func):
        def wrapper(self, *args, **kwargs):
            self.client.login(
                username='testuser',
                password='qwerty'
            )
            func(self, *args, **kwargs)
            self.client.logout()

        return wrapper

    def setUp(self):
        self.user = User(
            username='testuser',
            email='user@test.ru',
            password='qwerty'
        )
        self.user.set_password('qwerty')
        self.user.full_clean()
        self.user.save()

        super().setUp()

    def tearDown(self):
        User.objects.all().delete()

        super().tearDown()

    @login
    def test_profile_with_auth(self):
        response = self.client.get(self.PROFILE_URL, follow=True)

        self.assertEqual(
            response.redirect_chain, [],
            'Произошел редирект авторизованного юзера при запросе профиля'
        )
        self.assertIn(
            'games_winners', response.context,
            'Не передаются игры'
        )
        self.assertEqual(
            len(response.context['games_winners']), 0,
            'У пустого пользователя появились игры'
        )

    def test_profile_with_no_auth(self):
        response = self.client.get(self.PROFILE_URL, follow=True)

        self.assertRedirects(
            response, self.LOGIN_URL,
            msg_prefix='Неавторизованный смог зайти в профиль'
        )

    @login
    def test_login_with_auth(self):
        response = self.client.get(self.LOGIN_URL, follow=True)

        self.assertRedirects(
            response, self.PROFILE_URL,
            msg_prefix='Авторизованный пользователь смог '
                       'зайти на страницу логина'
        )

    @login
    def test_register_with_auth(self):
        response = self.client.get(self.REGISTER_URL, follow=True)

        self.assertRedirects(
            response, self.PROFILE_URL,
            msg_prefix='Авторизованный пользователь смог '
                       'зайти на страницу регистрации'
        )

    def test_login_with_no_auth(self):
        response = self.client.get(self.LOGIN_URL, follow=True)

        self.assertEqual(
            response.redirect_chain, [],
            'Произошел редирект неавторизованного юзера при запросе логина'
        )
        self.assertIn(
            'form', response.context,
            'Не передается форма'
        )
        for field in 'username', 'password':
            self.assertIn(
                field, response.context['form'].fields,
                'В форме нет {}'.format(field)
            )

    def test_register_with_no_auth(self):
        response = self.client.get(self.REGISTER_URL, follow=True)

        self.assertEqual(
            response.redirect_chain, [],
            'Произошел редирект неавторизованного юзера при запросе '
            'регистрации'
        )
        self.assertIn(
            'form', response.context,
            'Не передается форма'
        )
        for field in 'username', 'password1', 'password2':
            self.assertIn(
                field, response.context['form'].fields,
                'В форме регистрации нет {}'.format(field)
            )
