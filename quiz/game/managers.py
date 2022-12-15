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
