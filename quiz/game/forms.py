from django import forms

from . import models


class RoundStartForm(forms.Form):
    ...


class AddMemberForm(forms.ModelForm):
    class Meta:
        model = models.GameMember
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }


class StartGameForm(forms.ModelForm):
    class Meta:
        model = models.Game
        fields = ['start_round_time']
        widgets = {
            'start_round_time': forms.TextInput(
                attrs={'class': 'form-control'})
        }


class QuestionForm(forms.Form):
    CHOICES = (
        (0, "Не верно"),
        (1, "Верно"),
        (2, "Банк"),
    )

    answer = forms.ChoiceField(choices=CHOICES, label="Ответ")
