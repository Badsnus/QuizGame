import datetime

from django.db import models
from django.shortcuts import get_object_or_404


class GameMemberManager(models.Manager):

    def _select_related_game(self):
        return self.get_queryset().select_related('game')

    def members_by_game(self, game, out_of_game=None, order_by_pk=None):
        query = self.get_queryset().filter(game=game)

        if out_of_game is None:
            query = query.order_by('out_of_game')
        else:
            query = query.filter(out_of_game=out_of_game)

        if order_by_pk:
            query = query.order_by('pk')

        return query

    def winners_of_user_games(self, user):
        return (
            self._select_related_game()
            .filter(
                game__owner=user,
                game__ended=True,
                out_of_game=False
            ).order_by('-pk')
        )

    def end_game_members(self, game_pk):
        return (
            self._select_related_game().filter(
                game__pk=game_pk
            ).order_by('out_of_game')
        )

    def _get_game_members_no_end_game_by_user(self, user):
        return (
            self.get_queryset().filter(
                game__owner=user,
                game__ended=False,
            )
        )

    def get_game_members_by_user(self, user):
        return self._get_game_members_no_end_game_by_user(user).filter(
            game__started=False
        )

    def get_active_game_members_by_user(self, user):
        return self._get_game_members_no_end_game_by_user(user).filter(
            game__started=True,
            out_of_game=False
        ).order_by('pk')

    def user_for_question(self, user, offset):
        return (
            self.get_active_game_members_by_user(user)[offset]
        )

    def delete_game_member(self, pk):
        return (
            self.get_queryset().filter(pk=pk).delete()
        )

    def reset_stat(self, game_round, end_round=False):

        if end_round:
            game_round.ended = True

        game_round.offset = 0
        game_round.save(update_round_time=True)

        return self.get_queryset().filter(
            game=game_round.game,
            out_of_game=False
        ).update(brought_in_bank=0, bad_answers=0, good_answers=0)

    def set_out_of_game(self, pk):
        member = get_object_or_404(
            self.get_queryset().filter(pk=pk)
        )
        member.out_of_game = True
        member.save()
        return member


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

    def create_new_or_get_game(self, user):
        return self.get_queryset().get_or_create(
            owner=user,
            started=False,
            ended=False
        )


class GameRoundManager(models.Manager):
    def _select_related_game(self):
        return self.get_queryset().select_related('game')

    def find_round_by_game(self, game):
        return self._select_related_game().filter(
            ended=False,
            game=game
        ).first()

    def find_round_by_user(self, user, query_set=False, final=None):
        query = self._select_related_game().filter(
            ended=False,
            game__owner=user,
            game__started=True,
            game__ended=False
        )

        if final is not None:
            query = query.filter(final=final)

        if not query_set:
            query = query.first()
        return query

    def create_round(self, game):
        return self.get_queryset().create(
            game=game,
            end_time=(
                    datetime.datetime.utcnow() +
                    datetime.timedelta(seconds=game.round_time)
            )
        )


class GameQuestionManager(models.Manager):
    def _get_question(self, ids):
        return self.get_queryset().exclude(
            id__in=ids
        ).order_by("?").first()

    def get_random_question(self, used_questions):
        query = self._get_question(used_questions.values('question__pk'))
        if query:
            return query
        used_questions.delete()
        return self._get_question([])


class QuestionInGameManager(models.Manager):
    def get_by_game(self, game):
        return self.get_queryset().filter(
            game=game
        )
