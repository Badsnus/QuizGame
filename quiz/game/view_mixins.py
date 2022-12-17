from django.shortcuts import redirect, get_object_or_404

from . import models


class RedirectViewMixin:
    @staticmethod
    def get_redirect_url(game_round,
                         check_vote=True,
                         check_question=False,
                         check_final=False):
        if not game_round:
            return redirect('game:round_start')

        if check_vote and not game_round.vote:
            return redirect('game:question')

        if check_question and game_round.vote:
            return redirect('game:vote')

        if check_final and not game_round.final:
            return redirect('game:vote')


class GameFormInitialMixin:
    def get_initial(self):
        initial = super().get_initial()

        initial['game'] = get_object_or_404(
            models.Game.objects.no_ended_game_by_user(
                self.request.user,
                start=False,
                query_set=True
            )
        )

        return initial
