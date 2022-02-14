from .models import Partnerprofile, Contract, PaymentCode
from django import forms
from django.core.exceptions import ValidationError
from kkt_check.models import Kkt

TARIF_CHOICES =(
    (12, "12 месяцев"),
    (1, "1 месяц"),
    (3, "Квартал"),
)


class PartnerProfileEditForm(forms.ModelForm):
    """Форма редактирования профиля партнера"""

    inn = forms.CharField(label='ИНН партнёра', max_length=12, required=False)
    ur_adress = forms.CharField(label='Юридический адрес партнера', max_length=200, required=False)
    post_adress = forms.CharField(label='Почтовый адрес партнера', max_length=200, required=False)
    contacts = forms.CharField(label='Контактная информация для клиентов Партнера', max_length=200, required=False)

    class Meta:
        model = Partnerprofile
        fields = ('inn', 'ur_adress', 'post_adress', 'contacts')
        help_texts = {
            'inn': 'Заполнение поля необходимо для заказа кодов активации тарифа',
            'post_adress': 'Адрес для отправки документов',
            'contacts': 'Информация для связи клиентов с партнером'
        }


class NewContractForm(forms.Form):
    """Форма контракта партнера с кассой"""
    inn_kkt = forms.CharField(label='ИНН клиента', max_length=12)
    fn_number = forms.CharField(label='Заводской номер ФН кассы', max_length=16)

    def clean(self):
        """Проверка наличия ККТ с таким номером и ИНН"""
        cleaned_data = super().clean()
        inn_kkt = cleaned_data.get('inn_kkt')
        fn_number = cleaned_data.get('fn_number')
        if fn_number and inn_kkt:
            # Поиск кассы по регистрационному номеру
            try:
                kkt = Kkt.objects.get(fn_number=fn_number)
            except Kkt.DoesNotExist:
                raise ValidationError('ККТ с заводским номером ФН с таким номером не обнаружено')
            if kkt.inn_kkt != inn_kkt:
                raise ValidationError('ИНН пользователя не соответствует номеру кассы')


class PaymentContractForm(forms.Form):
    """Форма оплаты контракта кодом активации тарифа"""
    payment_code = forms.CharField(label='Код активации тарифа кассы', max_length=12)

    def clean(self):
        """Проверка наличия кода с таким номером"""
        cleaned_data = super().clean()
        code = cleaned_data.get('payment_code')
        if code:
            # Поиск кода в пуле кодов
            try:
                code = PaymentCode.objects.get(code=code)
            except PaymentCode.DoesNotExist:
                raise ValidationError('Код активации не обнаружено')


class MakeCodeOrderForm(forms.Form):
    """Форма заказа кодов активации тарифа"""
    num_payment_code = forms.IntegerField(label='Количество необходимых кодов')
    mounth_payment_count = forms.ChoiceField(choices=TARIF_CHOICES, label='Срок оплаты тарифа')
