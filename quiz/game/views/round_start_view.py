from django.shortcuts import get_object_or_404
from django.views import generic

from game import models


class RoundStartView(generic.TemplateView):
    template_name = 'game/start_round.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        game = get_object_or_404(models.Game, owner=self.request.user,
                                 started=True, ended=False)
        members = models.GameMember.objects.filter(
            game=game
        ).order_by('out_of_game')

        context['members'] = members
        context['round_number'] = members.filter(out_of_game=True).count() + 1
        context['round_time'] = game.start_round_time - 10 * (
                context['round_number'] - 1
        )

        return context
