import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from settings.settings import BANK
from . import models

User = get_user_model()


class StaticURLTests(TestCase):
    test_user = 'testuser'
    test_user_password = 'qwerty'
    test_user2 = 'testuser2'

    NO_AUTH_URL = reverse('game:no_auth')
    LOGIN_URL = reverse('users:login')
    START_GAME_URL = reverse('game:game_start')
    ADD_MEMBER_URL = reverse('game:add_member')
    START_ROUND_URL = reverse('game:round_start')
    QUESTION_URL = reverse('game:question')
    VOTE_URL = reverse('game:vote')
    FINAL_URL = reverse('game:final')

    @staticmethod
    def use_user(username):
        def login(func):
            def wrapper(self, *args, **kwargs):
                self.client.login(
                    username=username,
                    password=self.test_user_password
                )
                func(self, *args, **kwargs)
                self.client.logout()

            return wrapper

        return login

    def setUp(self):
        self.user = User(
            username=self.test_user
        )
        self.user.set_password(self.test_user_password)
        self.user.full_clean()
        self.user.save()

        self.user2 = User(
            username=self.test_user2
        )
        self.user2.set_password(self.test_user_password)
        self.user2.full_clean()
        self.user2.save()

        self.user2_game = models.Game.objects.create_new_or_get_game(
            self.user2
        )[0]
        for i in range(3):
            models.GameMember.objects.create(
                game=self.user2_game,
                name=f'chel {i}'
            )

        for i in range(3):
            models.GameQuestion.objects.create(question='123', answer='123')

        super().setUp()

    def tearDown(self):
        User.objects.all().delete()

        models.Game.objects.all().delete()
        models.GameMember.objects.all().delete()
        models.GameQuestion.objects.all().delete()
        models.GameRound.objects.all().delete()

        super().tearDown()

    def test_start_game_with_no_auth(self):
        response = self.client.get(self.START_GAME_URL, follow=True)
        self.assertRedirects(response, self.NO_AUTH_URL)

    def test_game_create_with_no_auth(self):
        response = self.client.post(self.START_GAME_URL, follow=True)
        self.assertRedirects(response, self.NO_AUTH_URL)

    def test_game_logic_no_auth(self):
        urls = (
            self.START_ROUND_URL, self.QUESTION_URL,
            self.VOTE_URL, self.FINAL_URL
        )
        for url in urls:
            for i in 'get', 'post':
                response = getattr(self.client, i)(
                    url,
                    follow=True
                )
                self.assertRedirects(
                    response,
                    self.LOGIN_URL + f'?next={url}'
                )

    @use_user(test_user)
    def test_game_logic_auth_no_game(self):
        urls = (
            self.START_ROUND_URL, self.QUESTION_URL,
            self.VOTE_URL, self.FINAL_URL
        )
        for url in urls:
            for i in 'get', 'post':
                response = getattr(self.client, i)(
                    url,
                    follow=True
                )
                self.assertRedirects(
                    response,
                    self.START_GAME_URL
                )

    @use_user(test_user)
    def test_start_game_with_auth_no_members(self):
        response = self.client.get(self.START_GAME_URL, follow=True)

        self.assertEqual(
            response.redirect_chain, [],
            'Произошел редирект авторизованного юзера при запросе профиля'
        )

        self.assertNotEqual(
            models.Game.objects.no_ended_game_by_user(self.user, start=False),
            None, 'Не создалась игра'
        )

        self.assertIn('form', response.context)
        self.assertIn('members', response.context)
        self.assertIn('member_form', response.context)

        response = self.client.post(self.START_GAME_URL, follow=True)

        self.assertEqual(
            models.Game.objects.no_ended_game_by_user(self.user, start=True),
            None, 'Создалась игра без участников'
        )

        for i in range(3):
            response = self.client.post(
                self.ADD_MEMBER_URL,
                data={'name': f'member {i}'},
                follow=True
            )
            self.assertRedirects(response, self.START_GAME_URL)
            self.assertEqual(
                models.GameMember.objects.get_game_members_by_user(
                    self.user
                ).count(),
                i + 1, 'Юзер не создается'
            )
        members_count = len(response.context['members'])
        member = response.context['members'].first()

        response = self.client.post(
            reverse('game:delete_member', kwargs=dict(pk=member.pk)),
            follow=True
        )
        self.assertRedirects(response, self.START_GAME_URL)
        members = models.GameMember.objects.get_game_members_by_user(
            self.user
        )
        self.assertNotIn(member, members, 'Юзер не удалился')
        self.assertEqual(
            members.count(), members_count - 1,
            'Появился какой-то левый юзер'
        )

        response = self.client.post(
            self.START_GAME_URL, follow=True,
            data={'round_time': 150}
        )
        self.assertRedirects(response, self.START_ROUND_URL)

        self.assertNotEqual(
            models.Game.objects.no_ended_game_by_user(self.user, start=True),
            None, 'Не создалась игра'
        )

    @use_user(test_user2)
    def test_game_logic(self):
        response = self.client.get(self.START_GAME_URL, follow=True)

        self.assertEqual(
            response.redirect_chain, [],
            'Произошел редирект авторизованного юзера при запросе профиля'
        )
        self.assertEqual(
            models.Game.objects.no_ended_game_by_user(self.user2, start=False),
            self.user2_game, 'Создалась какая-то другая игра'
        )
        test_data = (
            'form', 'members', 'member_form'
        )
        for key in test_data:
            self.assertIn(key, response.context, f'Нет {key} в старте игры')

        response = self.client.post(
            self.START_GAME_URL, follow=True,
            data={'round_time': 150}
        )
        self.assertRedirects(response, self.START_ROUND_URL)

        self.assertNotEqual(
            models.Game.objects.no_ended_game_by_user(self.user2, start=True),
            None, 'Не создалась игра'
        )
        test_data = (
            ('round_number', 1), ('round_time', 150), ('bank', 0)
        )
        for key, value in test_data:
            self.assertIn(key, response.context, f'Нет {key} в старте раунда')
            self.assertEqual(response.context[key], value)

        response = self.client.post(self.START_ROUND_URL, follow=True)

        self.assertRedirects(response, self.QUESTION_URL)
        self.assertNotEqual(
            models.GameRound.objects.find_round_by_game(self.user2_game),
            None, 'Не создался раунд'
        )

        test_data = (
            'round', 'member', 'round_end_time', 'question'
        )
        for key in test_data:
            self.assertIn(key, response.context, f'Нет {key} в вопрос вью')
        member = response.context['member']
        question = response.context['question']
        # without value
        response = self.client.post(self.QUESTION_URL, follow=True)
        self.assertRedirects(response, self.QUESTION_URL)
        self.assertEqual(
            response.context['member'], member,
            'Игрок поменялся без ответа'
        )

        # with good value
        response = self.client.post(
            self.QUESTION_URL, follow=True,
            data={
                'value': 'good',
                'question_pk': question.pk
            }
        )
        self.assertRedirects(response, self.QUESTION_URL)
        self.assertNotEqual(
            response.context['member'], member,
            'Игрок не поменялся после ответа'
        )
        self.assertEqual(
            models.GameMember.objects.get(pk=member.pk).good_answers, 1,
            'Не прибавился правильный ответ'
        )
        self.assertEqual(
            response.context['round'].now_bank, BANK[1],
            'Не добавился текуший банк'
        )
        member = response.context['member']
        question = response.context['question']

        # with bad value
        response = self.client.post(
            self.QUESTION_URL, follow=True,
            data={
                'value': 'bad',
                'question_pk': question.pk
            }
        )
        self.assertRedirects(response, self.QUESTION_URL)
        self.assertNotEqual(
            response.context['member'], member,
            'Игрок не поменялся после ответа'
        )
        self.assertEqual(
            models.GameMember.objects.get(pk=member.pk).bad_answers, 1,
            'Не прибавился неправильный ответ'
        )
        self.assertEqual(
            response.context['round'].now_bank, 0,
            'Не обнулился текуший банк'
        )

        for i in range(3):
            response = self.client.post(
                self.QUESTION_URL, follow=True,
                data={'value': 'good'}
            )
        member = response.context['member']
        now_bank = response.context['round'].now_bank

        # with bank value
        response = self.client.post(
            self.QUESTION_URL, follow=True,
            data={'value': 'bank', 'question_pk': question.pk}
        )
        self.assertRedirects(response, self.QUESTION_URL)
        self.assertEqual(
            response.context['member'], member,
            'Игрок поменялся после банка'
        )
        self.assertEqual(
            models.GameMember.objects.get(pk=member.pk).brought_in_bank,
            now_bank,
            'Не прибавилось добавление в банк'
        )
        self.assertEqual(
            response.context['round'].now_bank, 0,
            'Не обнулился текуший банк'
        )
        self.assertEqual(
            response.context['round'].bank, now_bank,
            'Не добавился банк'
        )

        # test end round by full bank
        for i in range(8):
            response = self.client.post(
                self.QUESTION_URL, follow=True,
                data={'value': 'good', 'question_pk': question.pk}
            )
        self.assertRedirects(response, self.VOTE_URL)
        # test vote
        self.assertIn('members', response.context)

        kicked_member_pk = response.context['members'].first().pk

        response = self.client.post(
            reverse('game:kick_member', kwargs=dict(pk=kicked_member_pk)),
            follow=True
        )

        self.assertRedirects(response, self.START_ROUND_URL)
        kicked_member = models.GameMember.objects.get(pk=kicked_member_pk)
        self.assertEqual(
            kicked_member.out_of_game, True,
            'Участник не вылетел с игры'
        )
        self.assertNotIn(
            kicked_member,
            models.GameMember.objects.members_by_game(
                self.user2_game,
                out_of_game=False
            ),
            'Участник остался в игре'
        )
        test_data = (
            ('round_number', 2), ('round_time', 140), ('bank', BANK[-1])
        )
        for key, value in test_data:
            self.assertIn(key, response.context, f'Нет {key} в старте раунда')
            self.assertEqual(response.context[key], value)

        self.client.post(self.START_ROUND_URL, follow=True)
        for value in 'good', 'bank':
            self.client.post(
                self.QUESTION_URL, follow=True,
                data={'value': value, 'question_pk': question.pk}
            )

        for i in range(3):
            self.client.post(
                self.QUESTION_URL, follow=True,
                data={'value': 'good', 'question_pk': question.pk}
            )

        # check end round by time
        game_round = models.GameRound.objects.find_round_by_game(
            self.user2_game
        )
        game_round.end_time = datetime.datetime(2000, 1, 1)
        game_round.save()
        response = self.client.post(
            self.QUESTION_URL, follow=True,
            data={'value': 'bank', 'question_pk': question.pk}
        )
        self.assertRedirects(response, self.FINAL_URL)

        test_data = (
            'question_for_member', 'members', 'bank', 'question'
        )
        for key in test_data:
            self.assertIn(key, response.context, f'Нет {key} в финале')

        # bank = first_round_bank + last_round_bank * 2 = 50k + 1k *2 = 52k
        # in general situation bank = sum(all_rounds) + last_round
        # all_rounds include last_round => last_round * 2
        self.assertEqual(
            response.context['bank'], 52000,
            'Добавился банк после времени'
        )

        for value in ('good', 'good', 'bad', 'bad') * 3:
            response = self.client.post(
                self.FINAL_URL, follow=True,
                data={'value': value, 'question_pk': question.pk}
            )
            self.assertRedirects(response, self.FINAL_URL)

        self.assertEqual(
            models.GameMember.objects.members_by_game(self.user2_game).filter(
                good_answers=3, bad_answers=3
            ).count(), 2, 'Не правильно считает ответы в финале'
        )
        member = response.context['question_for_member']
        for value in 'good', 'bad':
            response = self.client.post(
                self.FINAL_URL, follow=True,
                data={'value': value, 'question_pk': question.pk}
            )
        self.assertRedirects(
            response,
            reverse('game:result', kwargs=dict(pk=self.user2_game.pk))
        )
        self.assertIn('members', response.context)
        self.assertEqual(
            member, response.context['members'].first(),
            'Не правильный победитель'
        )
