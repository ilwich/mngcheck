from django.db import models, IntegrityError
from django.conf import settings
from django.contrib.auth.models import User
from kkt_check.models import Kkt
import datetime
from icecream import ic
import pytz
from dateutil.relativedelta import relativedelta
from django.utils.crypto import get_random_string
import string


# Create your models here.
class Partnerprofile(models.Model):
    """Описание профиля компании партнера"""

    # Пользователь
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Юридический адрес
    ur_adress = models.CharField(max_length=300, blank=True, null=True)
    # Почтовый адрес
    post_adress = models.CharField(max_length=300, blank=True, null=True)
    # Контакты для клиентов
    contacts = models.CharField(max_length=250, blank=True, null=True)
    # ИНН партнера
    inn = models.CharField(max_length=12, blank=True, null=True)

    def __str__(self):
        return f'Партнер: {self.user.profile.legal_entity} \n ИНН {self.inn}'


class Contract(models.Model):
    """Описание для договора клиентская касса - партнер"""

    # Партнер владелец контракта
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # Касса предмет контракта
    kkt = models.ForeignKey(Kkt, on_delete=models.CASCADE)
    # Дата добавления
    date_added = models.DateTimeField(default=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
    # Дата окончания оплаты
    date_end_payment = models.DateTimeField(default=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
    # Статус оплаты
    payment_status = models.CharField(max_length=30, default='Не оплачен')

    def __str__(self):
        """Информация о контракте"""
        # Название владельца кассы
        client_name = self.kkt.owner.profile.legal_entity
        # ИНН владельца кассы
        kkt_inn = self.kkt.inn_kkt
        return f"Клиент: {client_name}  ИНН: {kkt_inn} \n {self.kkt}"

    def pay_contract(self, mounth_payment_count):
        """Продление контракта на количество месяцев"""
        # Увеличение даты на количество месяцев тарифа
        self.date_end_payment += relativedelta(months=mounth_payment_count)
        # Смена статуса контракта
        self.payment_status = 'Действует'
        self.save()
        # Смена даты оплаты тарифа кассы

        self.kkt.data_end_of_payment = self.date_end_payment
        self.kkt.save()

class PaymentCode(models.Model):
    """Описание кода оплаты тарифа"""

    # Партнер владелец кода
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # Занчение кода
    code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    # Дата добавления
    date_added = models.DateTimeField(default=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
    # Статус оплаты
    payment_status = models.CharField(max_length=30, default='Не активирован')
    # Колчество месяцев оплачиваемых кодом
    mounth_payment_count = models.IntegerField(default=12)

    def __str__(self):
        """Информация о коде"""
        # Название партнера кому сгенерирован код
        partner_name = self.owner.profile.legal_entity
        # ИНН владельца кассы
        payment_status = self.payment_status
        return f"Код выпущен партнёру {partner_name} \n Статус: {payment_status}"

    def save(self, *args, **kwargs):
        if self.code is None:
            # Генерация уникального кода если поле пустое
            while True:
                try:
                    self.code = get_random_string(12, allowed_chars=string.digits)
                    self.save()
                    break
                except IntegrityError:
                    pass
        super(PaymentCode, self).save(*args, **kwargs)


class CodeOrder(models.Model):
    """Описание заказа кодов оплаты тарифа"""

    class Tarif(models.IntegerChoices):
        Тариф_12_месяцев = 12
        Тариф_1_месяц = 1
        Тариф_квартал = 3


    # Партнер создатель заказа
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    # Количество кодов
    code_count = models.IntegerField(default=1)
    # Дата добавления
    date_added = models.DateTimeField(default=datetime.datetime.utcnow().replace(tzinfo=pytz.UTC))
    # Статус обработк заказа
    payment_status = models.CharField(max_length=30, default='Создан')
    # Колчество месяцев оплачиваемых кодами
    mounth_payment_count = models.IntegerField(choices=Tarif.choices, default=12)

    def __str__(self):
        data_added = self.date_added.strftime('%d/%m/%Y')
        return f'Заказ кодов на {self.mounth_payment_count} месяцев \n' \
               f'Количество кодов: {self.code_count} \n' \
               f'Статус заказа: {self.payment_status}\n' \
               f'Дата формирования заказа: {data_added}'
