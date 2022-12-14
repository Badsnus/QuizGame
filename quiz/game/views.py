import datetime

from django.views import generic
from django.shortcuts import redirect, reverse, get_object_or_404, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from settings.settings import BANK
from . import models, forms


class NoAuthView(generic.TemplateView):
    template_name = 'game/no_auth.html'


class ResultView(generic.DetailView):
    template_name = 'game/result.html'
    context_object_name = 'winner'

    def get_object(self, queryset=None):
        return get_object_or_404(
            models.GameMember.objects.select_related('game').filter(
                game__pk=self.kwargs['pk'],
                out_of_game=False
            ),
        )


class FinalView(generic.TemplateView):
    template_name = 'game/final.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        game = get_object_or_404(
            models.Game, owner=self.request.user,
            started=True, ended=False
        )
        game_round = get_object_or_404(
            models.GameRound, game=game, final=True
        )
        if game_round.ended:
            game.ended = True
            game.save()
            return redirect('result', game.pk)

        members = list(models.GameMember.objects.filter(
            game=game, out_of_game=False
        ).order_by('pk'))
        question = models.GameQuestion.objects.order_by("?").first()
        context['bank'] = game.bank
        context['members'] = members
        context['question_for_member'] = members[game_round.offset]
        context['question'] = question

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if isinstance(context, dict):
            return self.render_to_response(context)
        return context

    def post(self, request, *args, **kwargs):

        value = request.POST.get('value', None)
        if not value:
            return HttpResponse(status=404)
        game_round = get_object_or_404(
            models.GameRound, game__owner=self.request.user,
            game__started=True, game__ended=False, final=True
        )
        members = list(models.GameMember.objects.filter(
            game__owner=self.request.user,
            game__started=True, game__ended=False, out_of_game=False
        ).order_by('pk'))
        player = members[game_round.offset]
        if (sum(
                sum(getattr(item, atr) for atr in
                    ['good_answers', 'bad_answers']) for item in
                members) < 9 or game_round.offset == 0):
            if value == 'good':
                player.good_answers += 1
            else:
                player.bad_answers += 1
        else:
            player1 = members[0]
            if value == 'good':
                player.good_answers += 1
            else:
                player.bad_answers += 1
            if player1.good_answers != player.good_answers:
                game_round.ended = True
                if player1.good_answers > player.good_answers:
                    player.out_of_game = True
                else:
                    player1.out_of_game = True
                    player1.save()

        game_round.offset = int(not game_round.offset)
        game_round.save()
        player.save()

        return redirect('final')


class VoteView(generic.TemplateView):
    template_name = 'game/vote.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        game = get_object_or_404(
            models.Game, owner=self.request.user,
            started=True, ended=False
        )
        game_round = get_object_or_404(
            models.GameRound, game=game, vote=True, ended=False
        )
        members = models.GameMember.objects.filter(
            game=game, out_of_game=False
        )
        context['members'] = members

        return context

    def get(self, request, *args, **kwargs):
        game_round = models.GameRound.objects.select_related('game').filter(
            ended=False,
            game__owner=self.request.user,
            game__started=True,
            game__ended=False,
            final=True
        ).first()
        if game_round:
            game_round.offset = 0
            game_round.save()
            models.GameMember.objects.filter(
                game=game_round.game,
                out_of_game=False
            ).update(brought_in_bank=0, bad_answers=0, good_answers=0)
            return redirect('final')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        game_round = models.GameRound.objects.select_related('game').filter(
            ended=False,
            game__owner=self.request.user,
            game__started=True,
            game__ended=False,
        ).first()

        if not game_round:
            return redirect('round_start')
        if game_round.vote is False:
            return redirect('question')

        member = get_object_or_404(
            models.GameMember,
            pk=kwargs.get('pk', None)
        )
        member.out_of_game = True
        member.save()
        game_round.ended = True
        game_round.save()
        models.GameMember.objects.filter(
            game=game_round.game,
            out_of_game=False
        ).update(brought_in_bank=0, bad_answers=0, good_answers=0)
        return redirect('round_start')


class QuestionView(LoginRequiredMixin, generic.DetailView):
    model = models.GameQuestion
    template_name = 'game/game.html'
    context_object_name = 'question'
    game_round = None

    def get_object(self, queryset=None):
        return models.GameQuestion.objects.order_by("?").first()

    def get(self, request, *args, **kwargs):
        self.game_round = get_object_or_404(
            models.GameRound,
            game__owner=self.request.user,
            ended=False
        )
        if self.game_round.vote:
            return redirect('vote')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_round = self.game_round
        member = models.GameMember.objects.filter(
            game__owner=self.request.user,
            game__ended=False,
            game__started=True,
            out_of_game=False
        ).order_by('id')[game_round.offset]

        context['round'] = game_round
        context['member'] = member

        context['round_end_time'] = str(game_round.end_time)

        return context

    def post(self, request, *args, **kwargs):
        value = request.POST.get('value', None)
        if value in {'bad', 'good', 'bank'}:
            game_round = get_object_or_404(
                models.GameRound.objects.prefetch_related('game'),
                game__owner=self.request.user,
                ended=False
            )
            members = models.GameMember.objects.filter(
                game__owner=self.request.user,
                game__ended=False,
                game__started=True,
                out_of_game=False
            ).order_by('pk')
            member = members[game_round.offset]

            if (game_round.end_time.replace(tzinfo=None) <=
                    datetime.datetime.utcnow().replace(tzinfo=None)):
                self.update_bank(game_round, game_round.bank, members, True)
                return redirect('question')

            if value in {'bad', 'good'}:
                if value == 'bad':
                    member.bad_answers += 1
                    game_round.now_bank = 0
                else:
                    member.good_answers += 1
                    game_round.now_bank = (
                        BANK[(BANK.index(game_round.now_bank) + 1) % len(BANK)]
                    )

                if game_round.offset + 1 != members.count():
                    game_round.offset += 1
                else:
                    game_round.offset = 0
            else:
                member.brought_in_bank = game_round.now_bank
                game_round.bank += game_round.now_bank
                game_round.now_bank = 0

            if game_round.now_bank >= BANK[-1]:
                self.update_bank(game_round, BANK[-1], members)

            game_round.save()
            member.save()
        return redirect('question')

    @staticmethod
    def update_bank(game_round, bank, members=None, vote=False):
        game = game_round.game
        game.bank += bank
        game_round.vote = True
        if members.count() == 2:
            game.bank += bank
            game_round.final = True
        game.save()
        if vote:
            game_round.save()


class AddMember(LoginRequiredMixin, generic.FormView):
    form_class = forms.AddMemberForm

    def form_valid(self, form):
        game = models.Game.objects.get_or_create(
            owner=self.request.user,
            started=False,
            ended=False
        )[0]

        models.GameMember.objects.create(
            game=game,
            name=form.cleaned_data['name']
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('game_start')


class RemoveMember(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        models.GameMember.objects.filter(
            id=kwargs['pk']
        ).delete()
        return redirect('game_start')


class StartGameView(generic.FormView):
    template_name = 'game/start_game.html'
    form_class = forms.StartGameForm

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('no_auth')
        game = models.Game.objects.filter(
            owner=request.user, started=True, ended=False
        )
        if game:
            return redirect('round_start')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        members = models.GameMember.objects.filter(
            game__owner=self.request.user,
            game__started=False,
            game__ended=False,
        )
        context['members'] = members
        context['member_form'] = forms.AddMemberForm
        return context

    def form_valid(self, form):
        game = models.Game.objects.filter(
            owner=self.request.user,
            started=False,
            ended=False
        ).first()
        count = models.GameMember.objects.filter(game=game).count()
        if 12 >= count >= 2:
            game.start_round_time = form.cleaned_data['start_round_time']
            game.started = True
            game.save()

            return super().form_valid(form)
        if count < 2:
            error = 'Минимальное кол-во игроков - 2'
        else:
            error = 'Максимальное кол-во игроков - 12'
        form.add_error('start_round_time', error)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('round_start')


class RoundStartView(generic.TemplateView):
    template_name = 'game/start_round.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        game = get_object_or_404(
            models.Game, owner=self.request.user,
            started=True, ended=False
        )
        members = models.GameMember.objects.filter(
            game=game
        ).order_by('out_of_game')
        context['members'] = members
        context['round_number'] = members.filter(out_of_game=True).count() + 1
        context['round_time'] = game.start_round_time - 10 * (
                context['round_number'] - 1
        )
        context['bank'] = game.bank
        return context

    def get(self, request, *args, **kwargs):
        started_round = models.GameRound.objects.filter(
            ended=False,
            game__owner=self.request.user,
            game__started=True,
            game__ended=False
        )
        if started_round:
            return redirect('question')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        game = get_object_or_404(
            models.Game, owner=self.request.user,
            started=True,
            ended=False,
        )
        x = models.GameRound.objects.get_or_create(
            game=game,
            ended=False
        )[0]
        if not x.end_time:
            members = models.GameMember.objects.filter(
                game=game
            )
            x.end_time = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=(game.start_round_time - 10 * (
                    members.filter(out_of_game=True).count()
                )))
            x.save()

        return redirect('question')
