from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):
    """Форма регистрации пользователя"""
    username = forms.CharField(label='Username')
    first_name = forms.CharField(label='Имя представителя')
    last_name = forms.CharField(label='Фамилия представителя')
    email = forms.EmailField(label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль (Должен состоять из белее чем 8 знаков. Букв и цифр.)', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')