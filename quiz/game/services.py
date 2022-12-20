import datetime

from django.shortcuts import get_object_or_404, redirect

from settings.settings import BANK
from . import models


class GameRoundLogic:

    @staticmethod
    def _get_redirect():
        return redirect('game:question')

    @staticmethod
    def _check_time(game_round):
        return (
                game_round.end_time.replace(tzinfo=None) <=
                datetime.datetime.utcnow().replace(tzinfo=None)
        )

    def update_round_info(self, user, value):
        if value in ('bad', 'good', 'bank'):
            game_round = get_object_or_404(
                models.GameRound.objects.find_round_by_user(user, True)
            )
            members = (
                models.GameMember.objects.get_active_game_members_by_user(
                    user
                )
            )

            member = members[game_round.offset]

            if self._check_time(game_round):
                self.make_vote(game_round, game_round.bank, members, True)
                return self._get_redirect()

            # TODO подумать мб можно проще
            if value in ('bad', 'good'):
                if value == 'bad':
                    member.bad_answers += 1
                    game_round.now_bank = 0
                else:
                    member.good_answers += 1
                    game_round.now_bank = (
                        BANK[(BANK.index(game_round.now_bank) + 1) % len(BANK)]
                    )

                game_round.offset = (game_round.offset + 1) % members.count()

            else:
                member.brought_in_bank = game_round.now_bank
                game_round.bank += game_round.now_bank
                game_round.now_bank = 0

            if game_round.now_bank + game_round.bank >= BANK[-1]:
                self.make_vote(game_round, BANK[-1], members)

            game_round.save()
            member.save()

        return self._get_redirect()

    @staticmethod
    def make_vote(game_round, bank, members=None, gm_save=None):
        game = game_round.game

        game.bank += bank
        game_round.vote = True

        if members.count() == 2:
            game.bank += bank
            game_round.final = True

        if gm_save:
            game_round.save()

        game.save()


class GameFinalLogic:
    @staticmethod
    def update_info(value, game_round):
        members = list(models.GameMember.objects.members_by_game(
            game=game_round.game, out_of_game=False, order_by_pk=True
        ))
        response_player = members[game_round.offset]

        answers_count = sum(
            sum(getattr(item, atr) for atr in ['good_answers', 'bad_answers'])
            for item in members
        )

        if value == 'good':
            response_player.good_answers += 1
        else:
            response_player.bad_answers += 1

        if not (answers_count < 9 or game_round.offset == 0):
            another_player = members[0]

            if another_player.good_answers != response_player.good_answers:
                game_round.ended = True

                if another_player.good_answers > response_player.good_answers:
                    user = response_player
                else:
                    user = another_player

                game_round.save(update_end_game=user)
                return redirect('game:result', game_round.game.pk)

        game_round.offset = int(not game_round.offset)
        game_round.save()
        response_player.save()
