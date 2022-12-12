from django import forms

from . import models


class AddMemberForm(forms.ModelForm):
    class Meta:
        model = models.GameMember
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }
