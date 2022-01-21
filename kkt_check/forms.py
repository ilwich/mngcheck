from django import forms
from .models import Kkt, Check_kkt, Check_good

class KktForm(forms.ModelForm):
    class Meta:
        model = Kkt
        fields = ['name', 'inn_kkt', 'fn_number', 'cashier_name', 'cashier_inn', 'tax_system', 'tax_code']
        labels = {'name': 'Название:', 'inn_kkt': 'ИНН владельца ККТ:', 'fn_number': 'Зав. № ФН',
                  'cashier_name': 'Ф.И.О. кассира', 'cashier_inn': 'ИНН кассира',
                  'tax_system': 'СНО по умолчанию', 'tax_code': 'Ставка НДС по умолчанию'}


class CheckForm(forms.ModelForm):
    class Meta:
        model = Check_kkt
        fields = ['buyer_name', 'buyer_inn', 'tax_system', 'send_check_to', 'cash', 'ecash']
        labels = {'buyer_name': 'Покупатель:', 'buyer_inn': 'ИНН покупателя:', 'tax_system': 'Система налогообложения',
                  'send_check_to': 'E-mail получателя', 'cash': 'Сумма наличными', 'ecash': 'Сумма безналичными'}
        help_texts = {
            'cash': 'Наличными от покупателя без точек в копейках', 'ecash': 'Безналичными от покупателя без точек в копейках'
        }


class GoodForm(forms.ModelForm):
    class Meta:
        model = Check_good
        fields = ['product_name', 'qty', 'tax_code', 'price', 'product_type_code']
        labels = {'product_name': 'Наименование товара/услуги:', 'qty': 'Количество:', 'tax_code': 'Тип ставки НДС (6 - без НДС):',
                  'price': 'Цена:', 'product_type_code': 'Предмет расчёта (1-Товар, 4-Услуга):'}
        help_texts = {
            'qty': 'Количество без точки 10000 = 1.00', 'price': 'Цена без точек в копейках'
        }
