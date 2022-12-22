from django import forms

from . import models


class AddMemberForm(forms.ModelForm):
    class Meta:
        model = models.GameMember
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

    def save(self, commit=True):
        self.instance.game = self.initial.get('game')
        return super().save(commit)


class StartGameForm(forms.ModelForm):
    class Meta:
        model = models.Game
        fields = ('round_time',)
        widgets = {
            'round_time': forms.NumberInput(
                attrs={'class': 'form-control'}
            )
        }

    def is_valid(self):
        members_count = models.GameMember.objects.members_by_game(
            self.initial.get('game')
        ).count()

        if members_count < 2:
            self.add_error('round_time', 'Минимальное кол-во игроков - 2')
        elif members_count > 12:
            self.add_error('round_time', 'Максимальное кол-во игроков - 12')

        return super().is_valid()

    def save(self, commit=True):
        self.instance = self.initial.get('game')
        self.instance.round_time = self.cleaned_data['round_time']
        self.instance.started = True
        if commit:
            self.instance.save()
