from django.db import models


class GameMemberManager(models.Manager):
    def winners_of_user_games(self, user):
        return (
            self.get_queryset().select_related('game').
            filter(
                game__owner=user,
                game__ended=True,
                out_of_game=False
            ).order_by('-pk')
        )
