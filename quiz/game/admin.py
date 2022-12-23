import csv
import io

from django.contrib import admin
from django.shortcuts import render, redirect
from import_export.admin import ImportExportModelAdmin

from .forms import CsvImportForm
from .models import GameQuestion, Game, GameMember


@admin.register(GameQuestion)
class QuestionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('question', 'answer')

    def import_action(self, request):
        form = CsvImportForm()

        if request.method == 'POST':
            GameQuestion.objects.import_csv(request.FILES, GameQuestion)

            return redirect("admin:game_gamequestion_changelist")

        context = {
            'form': form,
            'form_title': 'Загрузите CSV файл с вопросами.',
            'description': 'Содержимое файла: 1 колонка - вопрос, '
                           '2 колонка - ответ',
            'endpoint': '/admin/game/questions/import/'
        }

        return render(
            request, 'admin/import_game_questions.html', context
        )


class GameMemberInline(admin.StackedInline):
    model = GameMember
    extra = 0
    fields = ('name',)


@admin.register(Game)
class PersonAdmin(admin.ModelAdmin):
    inlines = (GameMemberInline,)
