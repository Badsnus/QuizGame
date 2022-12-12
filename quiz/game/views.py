from django.views import generic
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

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

        members_count = models.GameMember.objects.filter(game=game).count()

        models.GameMember.objects.create(
            game=game,
            name=form.cleaned_data['name'],
            member_id_in_game=members_count + 1
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('game_start')


class RemoveMember(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        models.GameMember.objects.filter(
            game__owner=request.user,
            game__ended=False,
            game__started=False,
            member_id_in_game=kwargs['pk']
        ).delete()
        return redirect('game_start')


class StartGameView(generic.TemplateView):
    template_name = 'game/start_game.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('no_auth')

        # TODO сдесь нужна провека на то есть ли у юзера начатая игра
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


class NoAuthView(generic.TemplateView):
    template_name = 'game/no_auth.html'
