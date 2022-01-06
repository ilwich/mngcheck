from django.db import models
from django.contrib.auth.models import User
from .serializers import GoodSerializer
from icecream import ic

# Create your models here.

class Kkt(models.Model):
    """касса, которой владеет пользователь"""
    #наименование кассы
    name = models.CharField(max_length=200)
    #дата добавления
    date_added = models.DateTimeField(auto_now_add=True)
    #инн владельца кассы
    inn_kkt = models.CharField(max_length=12)
    #номер текущего фискального накопителя
    fn_number = models.CharField(max_length=16)
    #имя кассира
    cashier_name = models.CharField(max_length=100, blank=True)
    #инн кассира
    cashier_inn = models.CharField(max_length=12, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Возвращает строковое представление модели."""
        return f"Касса {self.name} С ФН № {self.fn_number}"


class Check_kkt(models.Model):
    """Чеки пользователя на ККТ"""

    class Taxsystem(models.TextChoices):
        Общая = '0'
        Упрощенная_Доходы = '1'
        Упрощенная_Доходы_минус_Расходы = '2'
        Патент = '5'

    kkt = models.ForeignKey(Kkt, on_delete=models.CASCADE)
    shft_num = models.IntegerField(default=0)
    check_num = models.IntegerField(default=0)
    buyer_name = models.CharField(max_length=200, blank=True)
    buyer_inn = models.CharField(max_length=12, blank=True)
    tax_system = models.CharField(choices=Taxsystem.choices, max_length=1, default='0')
    send_check_to = models.CharField(max_length=50)
    cash = models.IntegerField(default=0)
    ecash = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='Добавлен')
    bot_message_id = models.CharField(max_length=40, default='0')

    class Meta:
        verbose_name_plural = 'kkts'

    def __str__(self):
        """Возвращает строковое представление чека."""
        return f"смена {str(self.shft_num)}_чек {str(self.check_num)}"

    def _get_kkt_buyer(self):
        """Возвращает словарь наименований покупателей из чеков key= инн покупателя"""
        # получаем все чеки по номеру кассы
        kkt_checks = self.kkt.check_kkt_set.all()
        if kkt_checks is not None:
            buyer_choice = {}
            for kkt_check in kkt_checks:
                # Проверка на повтор
                if kkt_check.buyer_inn not in buyer_choice.keys():
                     buyer_choice[kkt_check.buyer_inn] = kkt_check.buyer_name
        else:
            return None
        return buyer_choice

    def _get_kkt_buyer_email(self):
        """Возвращает список электронных адресов покупателей из чеков по инн покупателя"""
        # получаем все чеки по номеру кассы и ИНН пользователя
        kkt_checks = self.kkt.check_kkt_set.filter(buyer_inn=self.buyer_inn)
        if kkt_checks is not None:
            buyer_email = []
            for kkt_check in kkt_checks:
                # проверка на повторение
                if kkt_check.send_check_to not in buyer_email:
                     buyer_email.append(kkt_check.send_check_to)
        else:
            return None
        return buyer_email

    def _get_kkt_goods(self):
        """Возвращает список наименования номенклатуры для чека"""
        # получаем все чеки по номеру кассы
        kkt_checks = self.kkt.check_kkt_set.all()
        if kkt_checks is not None:
            goods_name_choice = []
            for kkt_check in kkt_checks:
                # Получаем список товаров из чека
                good_serialiser_for_queryset = GoodSerializer(kkt_check.checkkktset.all().values(), many=True)
                if good_serialiser_for_queryset is not None:
                    for good in good_serialiser_for_queryset.data:
                        # Проверка на повтор
                        if good['product_name'] not in goods_name_choice:
                            goods_name_choice.append(good['product_name'])
                else:
                    return None
        else:
            return None
        return goods_name_choice

    def _get_goods_summ(self):
        """Вычисление общей суммы номенклатуры в чеке"""
        # Получаем список товаров из чека и считем сумму
        good_serialiser_for_queryset = GoodSerializer(self.checkkktset.all().values(), many=True)
        good_serialiser_for_queryset.data
        if good_serialiser_for_queryset is not None:
            res_summ = 0
            for good in good_serialiser_for_queryset.data:
                res_summ += int(good['price'] * good['qty'] / 10000)
        else:
            return None
        return res_summ

    def get_text_of_check(self):
        """Вывод информации о чеке для проверки реквизитов"""
        res_text_list = []
        res_text_list.append(f'ККТ {self.kkt.name} ФН № {self.kkt.fn_number}')
        res_text_list.append(f'ИНН {self.kkt.inn_kkt} кассир {self.kkt.cashier_name}')
        res_text_list.append(f'ИНН Кассира {self.kkt.cashier_inn} ПРИХОД')
        if self.buyer_inn != '0000000000':
            res_text_list.append(f'Покупатель {self.buyer_name} ИНН {self.buyer_inn}')
        if self.send_check_to:
            res_text_list.append(f'Адрес отправки чека: {self.send_check_to}')
        # Получаем список товаров из чека и считем сумму
        good_for_queryset = self.checkkktset.filter(check_kkt=self)
        for good in good_for_queryset:
            res_text_list.append(f'{good.product_name}')
            ic(Check_good.Product_type.choices[1])
            good_type_code = [val[1] for val in Check_good.Product_type.choices if val[0] == good.product_type_code]
            good_tax_code = [val[1] for val in Check_good.Tax.choices if val[0] == good.tax_code]
            res_text_list.append(f'{good_type_code[0]} {good_tax_code[0]}')
            res_text_list.append(f'{good.qty/10000} x {good.price/100} = {int(good.price * good.qty / 1000000)}')
        res_text_list.append(f'ИТОГО: {self._get_goods_summ() / 100} руб.')
        res_text_list.append(f'Оплата - Наличными: {self.cash / 100} Безналичными: {self.ecash / 100}')
        tax_system = [val[1] for val in Check_kkt.Taxsystem.choices if val[0] == self.tax_system]
        res_text_list.append(f'СНО: {tax_system[0]}')
        return '\n'.join(res_text_list)


class Check_good(models.Model):
    """продажи в чек пользователя на ККТ"""

    class Product_type(models.IntegerChoices):
        Товар = 1
        Услуга = 4
        Платеж = 10

    class Tax(models.IntegerChoices):
        НДС_не_облагается = 6
        Ставка_НДС_20 = 1
        Ставка_НДС_10 = 2
        Ставка_НДС_0 = 5

    check_kkt = models.ForeignKey(Check_kkt, on_delete=models.CASCADE, related_name='checkkktset')
    product_name = models.CharField(max_length=200)
    qty = models.IntegerField(default=10000)
    tax_code = models.IntegerField(choices=Tax.choices, default=6)
    price = models.IntegerField()
    product_type_code = models.IntegerField(choices=Product_type.choices, default=1)

    def __str__(self):
        """Возвращает строковое представление товара."""
        summa = (self.qty * self.price) / 1000000
        return f"{self.product_name[:50]} на сумму {str(summa)}"