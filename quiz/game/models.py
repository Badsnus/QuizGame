from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User

from . import managers

class GameQuestion(models.Model):
    question = models.CharField(max_length=300)
    answer = models.CharField(max_length=300)


class GameMember(models.Model):
    objects = managers.GameMemberManager()

    name = models.CharField(max_length=30, verbose_name='имя')

    game = models.ForeignKey('Game', on_delete=models.CASCADE)

    good_answers = models.IntegerField(default=0)
    bad_answers = models.IntegerField(default=0)
    brought_in_bank = models.IntegerField(default=0)

    out_of_game = models.BooleanField(default=False)


class GameRound(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE)

    bank = models.IntegerField(default=0)
    now_bank = models.IntegerField(default=0)
    end_time = models.DateTimeField(null=True)
    vote = models.BooleanField(default=False)
    final = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)
    offset = models.IntegerField(default=0)


class Game(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    bank = models.IntegerField(default=0)
    start_round_time = models.IntegerField(
        default=150,
        verbose_name='начальное время на раунд',
        validators=[
            MaxValueValidator(1800),
            MinValueValidator(120)
        ]
    )

    started = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)
