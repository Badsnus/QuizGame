from django.views import generic

from .models import GameQuestion


class QuestionView(generic.DetailView):
    model = GameQuestion
    template_name = 'game/game.html'
    context_object_name = 'question'

    def get_object(self, queryset=None):
        return GameQuestion.objects.order_by("?").first()


class StartGameView(generic.TemplateView):
    template_name = 'game/start_game.html'
