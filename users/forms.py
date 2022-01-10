from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserForm(forms.ModelForm):
    """Форма регистрации пользователя"""
    username = forms.CharField(label='Username')
    first_name = forms.CharField(label='Имя представителя')
    last_name = forms.CharField(label='Фамилия представителя')
    email = forms.EmailField(label='Адрес электронной почты')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    """Форма редактирования профиля компании"""
    legal_entity = forms.CharField(label='Наименование компании или ИП для квитанции')
    personal_acc = forms.CharField(label='Расчётный счёт для указания в квитанции')
    bank_name = forms.CharField(label='Наименование банка для квитанции оплаты')
    bic = forms.CharField(label='БИК банка для квитанции')
    corres_acc = forms.CharField(label='Корр. счёт для указания в квитанции')

    class Meta:
        model = Profile
        fields = ('legal_entity', 'personal_acc', 'bank_name', 'bic', 'corres_acc')


class EditPassword(UserCreationForm):
    """Форма смены пароля пользователя"""
    password1 = forms.CharField(label='Пароль (Должен состоять из белее чем 8 знаков. Букв и цифр.)',
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
