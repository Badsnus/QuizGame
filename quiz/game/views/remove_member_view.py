from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic

from game import models


class RemoveMember(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        models.GameMember.objects.filter(
            id=kwargs['pk']
        ).delete()
        return redirect('game:game_start')
