from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.views import generic

from game import models
from game.forms import RoundStartForm


class RoundRunView(generic.FormView):
    template_name = "game/start_round.html"
    form_class = RoundStartForm

    def post(self, request, *args, **kwargs):
        ...


