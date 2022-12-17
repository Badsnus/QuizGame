from django.shortcuts import redirect


class RedirectViewMixin:
    @staticmethod
    def get_redirect_url(game_round, check_final=False):
        if not game_round:
            return redirect('game:round_start')

        if not game_round.vote:
            return redirect('game:question')

        if check_final and not game_round.final:
            return redirect('game:vote')
