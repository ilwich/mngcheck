from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from kkt_check.models import Check_kkt, Check_good

# Create your models here.
class Botuser(models.Model):
    """Модель телеграмм пользователя"""
    bot_user_id = models.IntegerField(unique=True, primary_key=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    bot_user_status = models.CharField(max_length=64, default='Авторизация')
    user_token = models.CharField(max_length=64)
    login_name = models.CharField(max_length=64)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=3)
    # Текущий чек для пользователя телеграмм
    current_сheck = models.ForeignKey(Check_kkt, on_delete=models.SET_NULL, null=True, blank=True)
    current_goods = models.ForeignKey(Check_good, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.bot_user_id}'

class Botmessage(models.Model):
    """Запись телеграмм сообщений"""
    update_id = models.IntegerField(unique=True)
    text = models.TextField(max_length=4096)
    date = models.DateTimeField(default=timezone.now)
    sender = models.ForeignKey(Botuser, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.text}'
