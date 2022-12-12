from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect


class ProfileView(generic.TemplateView):
    template_name = 'users/profile.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')
        return super().get(request, *args, **kwargs)


class RegisterView(generic.FormView):
    form_class = UserCreationForm
    template_name = 'registration/registration.html'
