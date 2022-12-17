from django.contrib import admin

from .models import GameQuestion, Game, GameMember

admin.site.register(GameQuestion)


class GameMemberInline(admin.StackedInline):
    model = GameMember
    extra = 0
    fields = ('name',)


@admin.register(Game)
class PersonAdmin(admin.ModelAdmin):
    inlines = (GameMemberInline,)
