from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import generic

from game import models
from game.forms import QuestionForm


class QuestionView(generic.TemplateView):
    template_name = 'game/game.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        game = get_object_or_404(
            models.Game,
            owner=self.request.user,
            started=True,
            ended=False
        )

        last_round = models.GameRound.objects.filter(
            game=game,
            answered=False
        ).last()

        if last_round and timezone.now() < last_round.end_time:
            context['member'] = last_round.member
            context['question'] = last_round.question
            context['form'] = QuestionForm()

            return context
        else:
            last_round = models.GameRound.objects.filter(game=game).last()

        if game.questions.count() == models.GameQuestion.objects.count():
            game.ended = True
            game.save()
            
            return None

        count_of_rounds = models.GameRound.objects.filter(
            game=game
        ).count()
        count_of_members = models.GameMember.objects.filter(
            game=game
        ).count()

        time_for_answer = game.start_round_time - 10 * count_of_rounds

        if time_for_answer <= 0:
            game.ended = True
            game.save()
            
            return None

        if count_of_rounds >= count_of_members:
            game.ended = True
            game.save()
            
            return None

        while True:
            question = models.GameQuestion.objects.order_by('?').first()

            if game.questions.filter(id=question.id).count() == 0:
                game.questions.add(question)
                break

        member = models.GameMember.objects.filter(
            game=game
        ).all()[count_of_rounds]

        round = models.GameRound(
            game=game,
            member=member,
            question=question,
            end_time=timezone.now() + timedelta(time_for_answer)
        )

        if last_round:
            round.bank = last_round.bank
            round.now_bank = last_round.now_bank

        round.save()

        context['time_for_answer'] = time_for_answer
        context['member'] = member
        context['question'] = question
        context['form'] = QuestionForm()

        return context
