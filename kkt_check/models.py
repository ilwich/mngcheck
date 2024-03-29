from django.db import models
from django.contrib.auth.models import User
from .serializers import GoodSerializer
from users.models import Profile
import datetime
from dateutil.relativedelta import relativedelta
from icecream import ic
import pytz

# Create your models here.

class Kkt(models.Model):
    """касса, которой владеет пользователь"""

    class Taxsystem(models.TextChoices):
        Общая = '0'
        Упрощенная_Доходы = '1'
        Упрощенная_Доходы_минус_Расходы = '2'
        Патент = '5'

    class Tax(models.IntegerChoices):
        НДС_не_облагается = 6
        Ставка_НДС_20 = 1
        Ставка_НДС_10 = 2
        Ставка_НДС_0 = 5

    # наименование кассы
    name = models.CharField(max_length=200)
    # дата добавления
    date_added = models.DateTimeField(auto_now_add=True)
    # инн владельца кассы
    inn_kkt = models.CharField(max_length=12)
    # номер текущего фискального накопителя
    fn_number = models.CharField(max_length=16, unique=True)
    # имя кассира
    cashier_name = models.CharField(max_length=100, blank=True)
    # инн кассира
    cashier_inn = models.CharField(max_length=12, blank=True)
    # пользователь владелец кассы
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # дата окончания оплаты сервиса по кассе добавлен месяц на проблный период
    data_end_of_payment = models.DateTimeField(
        default=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)+relativedelta(months=+1))
    # система налогообложения по умолчанию для чеков
    tax_system = models.CharField(choices=Taxsystem.choices, max_length=1, default='0')
    # ставка ндс по умолчанию для чеков
    tax_code = models.IntegerField(choices=Tax.choices, default=6)


    def __str__(self):
        """Возвращает строковое представление модели."""
        # Проверяем дату оплату с текущей
        kkt_payment_status = "Действует" if self.data_end_of_payment > datetime.datetime.utcnow().replace(tzinfo=pytz.UTC) else "Не оплачен"
        return f"КKT С ФН № {self.fn_number} {self.name}  тариф: {kkt_payment_status}"


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
    send_check_to = models.CharField(max_length=50, blank=True)
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
        kktname = f'ККТ {self.kkt.name}'
        # Разбиваем наименование кассы на строки по 50 символов
        res_text_list.extend([kktname[i:i + 40] for i in range(0, len(kktname), 40)])
        res_text_list.append(f'ФН {self.kkt.fn_number}')
        res_text_list.append(f'ИНН {self.kkt.inn_kkt}  ЧЕК ПРИХОДА')
        res_text_list.append(f'Кассир {self.kkt.cashier_name}')
        if self.buyer_inn != '':
            res_text_list.append(f'Покупатель: {self.buyer_name} \nПокупатель ИНН: {self.buyer_inn}')
        if self.send_check_to:
            res_text_list.append(f'e-mail получателя: {self.send_check_to}')
        # Получаем список товаров из чека и считем сумму
        good_for_queryset = self.checkkktset.filter(check_kkt=self)
        for good in good_for_queryset:
            # наименование товара
            res_text_list.append(f'{good.product_name}')
            res_text_list.append(f'{good.qty / 10000} x {good.price / 100} = {int(good.price * good.qty / 1000000)}')
            # Предмет расчёта и налог НДС
            good_type_code = [val[1] for val in Check_good.Product_type.choices if val[0] == good.product_type_code]
            good_tax_code = [val[1] for val in Check_good.Tax.choices if val[0] == good.tax_code]
            res_text_list.append(f'{good_type_code[0]} {good_tax_code[0]}')
        res_text_list.append(f'ИТОГО: {self._get_goods_summ() / 100}')
        res_text_list.append(f'Наличными: {self.cash / 100} \nБезналичными: {self.ecash / 100}')
        tax_system = [val[1] for val in Check_kkt.Taxsystem.choices if val[0] == self.tax_system]
        if 't=' in self.status:
            # дата из строки статуса чека
            dt = self.status[2:15]
            res_text_list.append(f'СНО: {tax_system[0]}')
            res_text_list.append(f'{dt[9:11]}:{dt[11:]} {dt[6:8]}-{dt[4:6]}-{dt[:4]}')
        else:
            res_text_list.append(f'СНО: {tax_system[0]}')
        return '\n'.join(res_text_list)

    def get_tax_system_for_check(self):
        """Возвращаем СНО для чека по умолчанию если задана"""
        try:
            # Получаем профиль пользователя кассы по чеку
            profile = Profile.objects.get(user=self.kkt.owner)
            # Проверяем установку в профиле для назначения СНО в чек
            if not profile.tax_system_from_client:
                return self.kkt.tax_system
            else:
                return False
        except:
            return False

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

    def get_tax_for_goods(self):
        """Возвращаем ставку НДС по умолчанию если задана"""
        try:
            # Получаем профиль пользователя кассы по товару в чеке
            profile = Profile.objects.get(user=self.check_kkt.kkt.owner)
            # Проверяем установку в профиле для назначения ставки НДС в чек
            if not profile.tax_from_client:
                return self.check_kkt.kkt.tax_code
            else:
                return False
        except:
            return False