from django.views import generic
from django.shortcuts import redirect, reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from . import models
from . import forms


class QuestionView(generic.DetailView):
    model = models.GameQuestion
    template_name = 'game/game.html'
    context_object_name = 'question'

    def get_object(self, queryset=None):
        return models.GameQuestion.objects.order_by("?").first()


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
        game = get_object_or_404(
            models.Game, owner=self.request.user, started=False,
            ended=False
        )
        game.started = True
        game.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('round_start')


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


class NoAuthView(generic.TemplateView):
    template_name = 'game/no_auth.html'
