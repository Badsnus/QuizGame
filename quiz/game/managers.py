from django.db import models
from django.shortcuts import get_object_or_404


class GameMemberManager(models.Manager):

    def _select_related_game(self):
        return self.get_queryset().select_related('game')

    def users_by_game(self, game):
        return self.get_queryset().filter(game=game).order_by('out_of_game')

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

    def get_game_members_by_user(self, user):
        return (
            self.get_queryset().filter(
                game__owner=user,
                game__started=False,
                game__ended=False,
            )
        )

    def delete_game_member(self, pk):
        return (
            self.get_queryset().filter(pk=pk).delete()
        )


class GameManager(models.Manager):

    def no_ended_game_by_user(self, user, start=True, query_set=False):
        query = (
            self.get_queryset().filter(
                owner=user,
                started=start,
                ended=False
            )
        )
        if not query_set:
            return query.first()
        return query


class GameRoundManager(models.Manager):
    def _select_related_game(self):
        return self.get_queryset().select_related('game')

    def find_round(self, user):
        return (
            self._select_related_game().filter(
                ended=False,
                game__owner=user,
                game__started=True,
                game__ended=False
            )
        ).first()
