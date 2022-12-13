from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView

from game import models
from game.forms import QuestionForm


class QuestionBankView(FormView):
    form_class = QuestionForm
    template_name = 'game/game.html'
    success_url = 'game:question'

    def form_valid(self, form):
        game = get_object_or_404(
            models.Game,
            owner=self.request.user,
            started=True,
            ended=False
        )
        last_round = models.GameRound.objects.filter(game=game).last()

        stats = (
            0,
            1000,
            2000,
            5000,
            10000,
            20000,
            30000,
            40000,
            50000,
        )

        try:
            new_bank = stats[stats.index(last_round.now_bank) + 1]
        except IndexError:
            new_bank = stats[-1]

        last_round.bank = new_bank
        last_round.now_bank = 0
        last_round.save()

        return HttpResponseRedirect(reverse(self.success_url))
