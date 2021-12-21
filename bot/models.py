from django.db import models
from django.utils import timezone

# Create your models here.
class Botuser(models.Model):
    """Модель телеграмм пользователя"""
    bot_user_id = models.IntegerField(unique=True, primary_key=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

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
