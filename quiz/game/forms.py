from django import forms

from . import models


class AddMemberForm(forms.ModelForm):
    class Meta:
        model = models.GameMember
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        self.instance.game = self.initial.get('game')
        return super().save(commit)


class StartGameForm(forms.ModelForm):
    class Meta:
        model = models.Game
        fields = ['round_time']
        widgets = {
            'round_time': forms.NumberInput(
                attrs={'class': 'form-control'}
            )
        }

    # def save(self, commit=True):
