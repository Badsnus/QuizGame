from django.views import generic


class NoAuthView(generic.TemplateView):
    template_name = 'game/no_auth.html'
