from django.views import generic
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from . import models, forms
from . import services
from .view_mixins import RedirectViewMixin, GameFormInitialMixin


class NoAuthView(generic.TemplateView):
    template_name = 'game/no_auth.html'


class StartGameView(GameFormInitialMixin, generic.FormView):
    template_name = 'game/start_game.html'
    form_class = forms.StartGameForm

    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('game:no_auth')

        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('game:no_auth')

        started_game = models.Game.objects.no_ended_game_by_user(
            user=request.user,
            start=True
        )

        if started_game:
            return redirect('game:round_start')

        models.Game.objects.create_new_or_get_game(request.user)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        members = models.GameMember.objects.get_game_members_by_user(
            self.request.user,
        )

        context['members'] = members
        context['member_form'] = forms.AddMemberForm
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('game:round_start')


class AddMember(LoginRequiredMixin, GameFormInitialMixin, generic.FormView):
    form_class = forms.AddMemberForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('game:game_start')


class RemoveMember(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        models.GameMember.objects.delete_game_member(kwargs['pk'])

        return redirect('game:game_start')


class RoundStartView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'game/start_round.html'
    game = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        members = models.GameMember.objects.members_by_game(self.game)

        round_number = members.filter(out_of_game=True).count()

        context['members'] = members
        context['round_number'] = round_number + 1
        context['round_time'] = self.game.round_time
        context['bank'] = self.game.bank

        return context

    def get(self, request, *args, **kwargs):
        self.game = models.Game.objects.no_ended_game_by_user(
            self.request.user
        )

        if not self.game:
            return redirect('game:game_start')

        started_round = models.GameRound.objects.find_round_by_game(
            game=self.game
        )

        if started_round:
            return redirect('game:question')

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        game_round = models.GameRound.objects.find_round_by_user(request.user)

        if not game_round:
            game = models.Game.objects.no_ended_game_by_user(
                request.user,
            )

            if not game:
                return redirect('game:game_start')

            models.GameRound.objects.create_round(game)

        return redirect('game:question')


class QuestionView(LoginRequiredMixin, generic.DetailView, RedirectViewMixin):
    model = models.GameQuestion
    template_name = 'game/game.html'
    context_object_name = 'question'
    game_round = None

    def get_object(self, queryset=None):
        return models.GameQuestion.objects.get_random_question()

    def get(self, request, *args, **kwargs):
        self.game_round = models.GameRound.objects.find_round_by_user(
            request.user
        )

        redirect_url = self.get_redirect_url(
            self.game_round,
            check_question=True,
            check_vote=False
        )

        if redirect_url:
            return redirect_url

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        member = models.GameMember.objects.user_for_question(
            self.request.user,
            self.game_round.offset
        )

        context['round'] = self.game_round
        context['member'] = member
        context['round_end_time'] = str(self.game_round.end_time) + ' UTC'

        return context

    def post(self, request, *args, **kwargs):
        game_logic = services.GameRoundLogic()

        return game_logic.update_round_info(
            request.user,
            request.POST.get('value', None)
        )


class VoteView(LoginRequiredMixin, generic.TemplateView, RedirectViewMixin):
    template_name = 'game/vote.html'
    game_round = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['members'] = models.GameMember.objects.members_by_game(
            self.game_round.game,
            out_of_game=False
        )

        return context

    def get(self, request, *args, **kwargs):

        self.game_round = models.GameRound.objects.find_round_by_user(
            request.user
        )
        redirect_url = self.get_redirect_url(self.game_round)

        if redirect_url:
            return redirect_url

        if self.game_round.final:
            models.GameMember.objects.reset_stat(self.game_round)

            return redirect('game:final')

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        game_round = models.GameRound.objects.find_round_by_user(request.user)

        redirect_url = self.get_redirect_url(game_round)

        if redirect_url:
            return redirect_url

        models.GameMember.objects.set_out_of_game(
            kwargs.get('pk', None)
        )

        models.GameMember.objects.reset_stat(game_round, True)

        return redirect('game:round_start')


class FinalView(LoginRequiredMixin, generic.TemplateView, RedirectViewMixin):
    template_name = 'game/final.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        game_round = models.GameRound.objects.find_round_by_user(
            self.request.user
        )
        redirect_url = self.get_redirect_url(game_round, check_final=True)

        if redirect_url:
            return redirect_url

        members = list(models.GameMember.objects.members_by_game(
            game=game_round.game, out_of_game=False, order_by_pk=True
        ))

        context['bank'] = game_round.game.bank
        context['members'] = members
        context['question_for_member'] = members[game_round.offset]
        context['question'] = models.GameQuestion.objects.get_random_question()

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if isinstance(context, dict):
            return self.render_to_response(context)
        return context

    def post(self, request, *args, **kwargs):

        value = request.POST.get('value', None)
        if value not in ('good', 'bad'):
            return redirect('game:final')

        game_round = models.GameRound.objects.find_round_by_user(
            self.request.user
        )
        redirect_url = self.get_redirect_url(game_round, check_final=True)

        if redirect_url:
            return redirect_url

        result = services.GameFinalLogic.update_info(value, game_round)

        return result if result else redirect('game:final')


class ResultView(generic.ListView):
    template_name = 'game/result.html'
    context_object_name = 'members'

    def get_queryset(self):
        return models.GameMember.objects.end_game_members(
            game_pk=self.kwargs['pk']
        )
