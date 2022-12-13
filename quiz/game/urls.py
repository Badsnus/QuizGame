from django.urls import path

from .views.add_member_view import AddMemberView
from .views.no_auth_view import NoAuthView
from .views.question_answer_view import QuestionAnswerView
from .views.question_bank_view import QuestionBankView
from .views.question_view import QuestionView
from .views.remove_member_view import RemoveMember
from .views.round_run_view import RoundRunView
from .views.round_start_view import RoundStartView
from .views.start_game_view import StartGameView

app_name = 'game'

urlpatterns = [
    path(
        'start/',
        StartGameView.as_view(),
        name='game_start'
    ),
    path(
        'add_member/',
        AddMemberView.as_view(),
        name='add_member'
    ),
    path(
        'delete_member/<int:pk>/',
        RemoveMember.as_view(),
        name='delete_member'
    ),
    path(
        'round_start/',
        RoundStartView.as_view(),
        name='round_start'
    ),
    path(
        'round_run/',
        RoundRunView.as_view(),
        name='round_run'
    ),
    path(
        'question/',
        QuestionView.as_view(),
        name='question'
    ),
    path(
        'question/answer/',
        QuestionAnswerView.as_view(),
        name='question_answer'
    ),
    path(
        'question/bank/',
        QuestionBankView.as_view(),
        name='question_bank'
    ),
    path(
        'no_auth/',
        NoAuthView.as_view(),
        name='no_auth'
    ),
]
