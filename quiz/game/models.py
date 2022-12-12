from django.db import models
from django.contrib.auth.models import User


class GameQuestion(models.Model):
    question = models.CharField(max_length=300)
    answer = models.CharField(max_length=300)


class GameMember(models.Model):
    name = models.CharField(max_length=30)

    member_id_in_game = models.IntegerField()
    game = models.ForeignKey('Game', on_delete=models.CASCADE)

    good_answers = models.IntegerField()
    bad_answers = models.IntegerField()
    brought_in_bank = models.IntegerField()


class Game(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    bank = models.IntegerField()

    round_time = models.IntegerField()
    end_round_time = models.FloatField()
