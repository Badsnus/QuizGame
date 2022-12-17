from django.contrib.auth import authenticate, login, views
from django.views import generic
from django.shortcuts import redirect, render

from game import models as game_models
from .forms import RegisterForm, LoginForm


class LoginView(views.LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return redirect('users:profile')
        return super().get(request, *args, **kwargs)


class CustomLogoutView(views.LogoutView):
    template_name = 'registration/logout.html'


class RegisterView(generic.FormView):
    form_class = RegisterForm
    template_name = 'registration/registration.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return redirect('users:profile')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()

        user = authenticate(
            username=form.cleaned_data.get('username'),
            password=form.cleaned_data.get('password1')
        )
        login(self.request, user)
        return redirect('users:profile')

    def form_invalid(self, form):
        context = {
            'form': form
        }
        return render(self.request, self.template_name, context)


class ProfileView(generic.TemplateView):
    template_name = 'users/profile.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('users:login')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['games_winners'] = (
            game_models.GameMember.objects.winners_of_user_games(
                self.request.user
            )
        )
        return context
