from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import generic

from game import forms, models


class AddMemberView(LoginRequiredMixin, generic.FormView):
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
        return reverse('game:game_start')
