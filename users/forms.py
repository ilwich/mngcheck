from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    """Форма регистрации пользователя"""
    username = forms.CharField(label="Имя пользователя для входа")
    email = forms.EmailField(label="Адрес электронной почты для восстановления пароля")

    class Meta:
        model = User
        fields = ('username', 'email', )

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        username = self.cleaned_data["username"]
        if commit:
            user.save()
        return user


class UserForm(forms.ModelForm):
    """Форма профиля пользователя"""
    username = forms.CharField(label='Username')
    first_name = forms.CharField(label='Имя представителя', required=False)
    last_name = forms.CharField(label='Фамилия представителя', required=False)
    email = forms.EmailField(label='Адрес электронной почты', required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    """Форма редактирования профиля компании"""
    legal_entity = forms.CharField(label='Наименование компании или ИП для квитанции', required=False)
    personal_acc = forms.CharField(label='Расчётный счёт для указания в квитанции', required=False)
    bank_name = forms.CharField(label='Наименование банка для квитанции оплаты', required=False)
    bic = forms.CharField(label='БИК банка для квитанции', required=False)
    corres_acc = forms.CharField(label='Корр. счёт для указания в квитанции', required=False)
    tax_from_client = forms.BooleanField(label='Ставку НДС указать при создании чека', required=False)
    tax_system_from_client = forms.BooleanField(label='СНО указать при создании чека', required=False)

    class Meta:
        model = Profile
        fields = ('legal_entity', 'personal_acc', 'bank_name', 'bic', 'corres_acc',
                  'tax_from_client', 'tax_system_from_client', 'client_status')
        labels = {'client_status': 'Статус клиента'}
        help_texts = {
            'client_status': 'Для продления тарифов на ККТ клиентов установите статус Партнёр'
        }

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['client_status'].choices = (
                (0, ( "Клиент" )),
                (1, ( "Партнер" )),
            )



class EditPassword(UserCreationForm):
    """Форма смены пароля пользователя"""
    password1 = forms.CharField(label='Пароль (Должен состоять из белее чем 8 знаков. Букв и цифр.)',
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
