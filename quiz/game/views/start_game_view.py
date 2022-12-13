from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views import generic

from game import models, forms


class StartGameView(generic.FormView):
    template_name = 'game/start_game.html'
    form_class = forms.StartGameForm

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('game:no_auth')
        game = models.Game.objects.filter(
            owner=request.user, started=True, ended=False
        )
        if game:
            return redirect('game:round_start')
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
        return reverse('game:round_start')
