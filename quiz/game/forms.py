from django import forms

from . import models


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(
        allow_empty_file=False,
        label='CSV файл',
        widget=forms.FileInput(attrs={'class': 'form-input'})
    )


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
        fields = ('round_time', 'question_filter')
        widgets = {
            'round_time': forms.NumberInput(
                attrs={'class': 'form-control'}
            ),
            'question_filter': forms.Select(
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
        self.instance.question_filter = self.cleaned_data['question_filter']
        self.instance.started = True
        if commit:
            self.instance.save()
