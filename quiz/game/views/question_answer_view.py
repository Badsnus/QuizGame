from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView

from game import models
from game.forms import QuestionForm


class QuestionAnswerView(FormView):
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

        if game.questions.count() == models.GameQuestion.objects.count():
            game.ended = True
            game.save()

            return HttpResponseRedirect(reverse(self.success_url))

        last_round = models.GameRound.objects.filter(
            game=game,
            answered=False
        ).last()

        if last_round and timezone.now() < last_round.end_time:
            if int(form.cleaned_data['answer']) == 1:
                last_round.member.good_answers += 1
                last_round.member.save()
            else:
                last_round.member.bad_answers += 1
                last_round.member.save()

                last_round.now_bank = 0
                last_round.save()
        else:
            last_round.member.out_of_game = True
            last_round.member.save()

            last_round.now_bank = 0
            last_round.save()

        last_round.answered = True
        last_round.save()

        return HttpResponseRedirect(reverse(self.success_url))
