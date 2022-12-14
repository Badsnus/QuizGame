from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect

from game import models as game_models


class ProfileView(generic.TemplateView):
    template_name = 'users/profile.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        games_winners = game_models.GameMember.objects.select_related(
            'game').filter(
            game__owner=self.request.user,
            game__ended=True,
            out_of_game=False
        ).order_by('-pk')
        context['games_winners'] = games_winners
        return context


class RegisterView(generic.FormView):
    form_class = UserCreationForm
    template_name = 'registration/registration.html'
