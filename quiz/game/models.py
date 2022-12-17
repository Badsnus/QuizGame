from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User

from . import managers


class GameQuestion(models.Model):
    objects = managers.GameQuestionManager()

    question = models.CharField(max_length=300, verbose_name='вопрос')
    answer = models.CharField(max_length=300, verbose_name='ответ')

    def __str__(self):
        return f'вопрос {self.pk}'

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'


class GameMember(models.Model):
    objects = managers.GameMemberManager()

    name = models.CharField(max_length=30, verbose_name='имя')

    game = models.ForeignKey(
        'Game',
        on_delete=models.CASCADE,
        verbose_name='игра'
    )

    good_answers = models.IntegerField(
        default=0,
        verbose_name='правильных ответов'
    )
    bad_answers = models.IntegerField(
        default=0,
        verbose_name='неправильных ответов'
    )
    brought_in_bank = models.IntegerField(
        default=0,
        verbose_name='принес в банк'
    )

    out_of_game = models.BooleanField(default=False, verbose_name='вылетел')

    def __str__(self):
        return f'участник {self.pk}'

    class Meta:
        verbose_name = 'участник'
        verbose_name_plural = 'участники'


class GameRound(models.Model):
    objects = managers.GameRoundManager()

    game = models.ForeignKey(
        'Game',
        on_delete=models.CASCADE,
        verbose_name='игра'
    )

    bank = models.IntegerField(default=0, verbose_name='банк')
    now_bank = models.IntegerField(default=0, verbose_name='текущий банк')
    end_time = models.DateTimeField(null=True, verbose_name='время окончания')
    vote = models.BooleanField(default=False, verbose_name='этап голосования')
    final = models.BooleanField(default=False, verbose_name='финальный раунд')
    ended = models.BooleanField(default=False, verbose_name='раунд закончился')
    offset = models.IntegerField(default=0, verbose_name='номер отвечающего')

    def __str__(self):
        return f'раунд {self.pk}'

    def save(self, update_round_time=False, update_end_game=None,
             *args, **kwargs):
        """
        :param update_round_time - bool
        :param update_end_game - None or user
        """
        if any((update_round_time, update_end_game)):
            if update_round_time:
                self.game.round_time -= 10
            elif update_end_game:
                update_end_game.out_of_game = True
                update_end_game.save()
                self.game.ended = True

            self.game.save()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'раунд'
        verbose_name_plural = 'раунды'


class Game(models.Model):
    objects = managers.GameManager()
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='владелец игры'
    )

    bank = models.IntegerField(default=0, verbose_name='банк')
    round_time = models.IntegerField(
        default=150,
        verbose_name='начальное время на раунд',
        validators=[
            MaxValueValidator(1800),
            MinValueValidator(120)
        ],
    )

    started = models.BooleanField(default=False, verbose_name='игра начата')
    ended = models.BooleanField(default=False, verbose_name='игра закончена')

    def __str__(self):
        return f'игра {self.pk}'

    class Meta:
        verbose_name = 'игра'
        verbose_name_plural = 'игры'
