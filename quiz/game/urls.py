from django.urls import path

from . import views

urlpatterns = [
    path('start/', views.StartGameView.as_view(), name='game_start'),
    path('question/', views.QuestionView.as_view(), name='question')
]
