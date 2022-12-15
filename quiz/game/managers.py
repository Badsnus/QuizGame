from django.db import models
from django.shortcuts import get_object_or_404


class GameMemberManager(models.Manager):

    def _select_related_game(self):
        return self.get_queryset().select_related('game')

    def winners_of_user_games(self, user):
        return (
            self._select_related_game()
            .filter(
                game__owner=user,
                game__ended=True,
                out_of_game=False
            ).order_by('-pk')
        )

    def winner(self, game_pk):
        return get_object_or_404(
            self._select_related_game().filter(
                game__pk=game_pk,
                out_of_game=False
            ),
        )

    def game_members(self, user):
        return (
            self.get_queryset().filter(
                game__owner=user,
                game__started=False,
                game__ended=False,
            )
        )


class GameManager(models.Manager):
    def user_started_game(self, user):
        return (
            self.get_queryset().filter(
                owner=user,
                started=True,
                ended=False
            )
        )
