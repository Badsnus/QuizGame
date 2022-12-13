from django.urls import path

from . import views

urlpatterns = [
    path('start/', views.StartGameView.as_view(), name='game_start'),
    path('add_member/', views.AddMember.as_view(), name='add_member'),
    path('delete_member/<int:pk>/', views.RemoveMember.as_view(),
         name='delete_member'),

    path('round_start/', views.RoundStartView.as_view(), name='round_start'),

    path('question/', views.QuestionView.as_view(), name='question'),

    path('no_auth/', views.NoAuthView.as_view(), name='no_auth'),
]
