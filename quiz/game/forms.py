from django import forms

from . import models


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
            'start_round_time': forms.NumberInput(
                attrs={'class': 'form-control'}
            )
        }
