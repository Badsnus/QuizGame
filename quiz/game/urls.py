from django.urls import path

from . import views

app_name = 'game'

urlpatterns = [
    path('no_auth/', views.NoAuthView.as_view(), name='no_auth'),

    path('start/', views.StartGameView.as_view(), name='game_start'),

    path('add_member/', views.AddMember.as_view(), name='add_member'),
    path('delete_member/<int:pk>/', views.RemoveMember.as_view(),
         name='delete_member'),

    path('round_start/', views.RoundStartView.as_view(), name='round_start'),

    path('question/', views.QuestionView.as_view(), name='question'),
    path('final/', views.FinalView.as_view(), name='final'),

    path('vote/', views.VoteView.as_view(), name='vote'),
    path('vote/kick/<int:pk>/', views.VoteView.as_view(), name='kick_member'),

    path('result/<int:pk>/', views.ResultView.as_view(), name='result'),
]
