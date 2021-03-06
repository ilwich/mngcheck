from django.db import models
from django.conf import settings


class Profile(models.Model):
    """Описание профиля компании"""

    # Описание типов клиента
    class Clientstatus(models.IntegerChoices):
        Клиент = 0
        Партнёр = 1
        Дилер = 2


    # Пользователь
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Название ИП или организации для квитанции
    legal_entity = models.CharField(max_length=300, blank=True, null=True)
    # Расчётный счёт
    personal_acc = models.CharField(max_length=20, blank=True, null=True)
    # Название банка
    bank_name = models.CharField(max_length=300, blank=True, null=True)
    # БИК банка
    bic = models.CharField(max_length=9, blank=True, null=True)
    # Корр. счёт
    corres_acc = models.CharField(max_length=20, blank=True, null=True)
    # Флаг настройки для выбора ставки ндс по умолчанию или от пользователя
    tax_from_client = models.BooleanField(default=True)
    # Флаг настройки для выбора системы налогообложения по умолчанию или от пользователя
    tax_system_from_client = models.BooleanField(default=True)
    # Статус партнера
    client_status = models.IntegerField(choices=Clientstatus.choices, default=0)

    def __str__(self):
        return 'Профиль для пользователя {}'.format(self.user.username)

    def get_qr_payment_data(self):
        """Формирование данных для qr-кода квитанции"""
        res = f'ST00012|' \
              f'Name={self.legal_entity}|' \
              f'PersonalAcc={self.personal_acc}|' \
              f'BankName={self.bank_name}|' \
              f'BIC={self.bic}|' \
              f'CorrespAcc={self.corres_acc}|'
        return res
