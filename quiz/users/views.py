from django.contrib.auth import authenticate, login, views, mixins
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic

from game import models as game_models
from .forms import RegisterForm, LoginForm, CustomPasswordChangeForm
from .mixins import LogoutRequiredMixin


class LoginView(LogoutRequiredMixin, views.LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'


class CustomLogoutView(views.LogoutView):
    template_name = 'registration/logout.html'


class RegisterView(LogoutRequiredMixin, generic.FormView):
    form_class = RegisterForm
    template_name = 'registration/registration.html'

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


class ProfileView(mixins.LoginRequiredMixin, generic.TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['games_winners'] = (
            game_models.GameMember.objects.winners_of_user_games(
                self.request.user
            )
        )
        return context


class CustomPasswordChangeDoneView(views.PasswordChangeDoneView):
    template_name = "users/password_change_done.html"


class CustomPasswordChangeView(views.PasswordChangeView):
    template_name = "users/password_change.html"
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy("users:change_password_done")
