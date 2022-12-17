from django import forms
from django.contrib.auth import get_user_model, forms as auth_forms, models

User = get_user_model()


class RegisterForm(auth_forms.UserCreationForm):
    username = auth_forms.UsernameField(
        label='Логин',
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'class': 'form-control',
                'placeholder': 'pronin_i_eremin'
            }
        )
    )
    password1 = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'class': 'form-control',
                'placeholder': 'Введите пароль'
            }
        ),
    )
    password2 = forms.CharField(
        label='Подтвердите пароль',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'class': 'form-control',
                'placeholder': 'Введите пароль еще раз'
            }
        ),
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class LoginForm(auth_forms.AuthenticationForm):
    username = auth_forms.UsernameField(
        widget=forms.TextInput(
            attrs={
                'autofocus': True,
                'class': 'form-control',
                'placeholder': 'pronin_i_eremin'
            }
        ),
        label='Логин'
    )
    password = forms.CharField(
        label=models._('Password'),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'current-password',
                'class': 'form-control',
                'placeholder': 'password'
            }
        ),
    )

    class Meta:
        model = User
        fields = ('username', 'password')
