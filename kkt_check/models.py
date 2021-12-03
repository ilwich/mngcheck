from django.db import models
from django.contrib.auth.models import User

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
    cashier_name = models.CharField(max_length=50)
    #инн кассира
    cashier_inn = models.CharField(max_length=12, default='0000000000')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Возвращает строковое представление модели."""
        return f"Касса {self.name} С ФН № {self.fn_number}"


class Check_kkt(models.Model):
    """Чеки пользователя на ККТ"""
    kkt = models.ForeignKey(Kkt, on_delete=models.CASCADE)
    shft_num = models.IntegerField(default=0)
    check_num = models.IntegerField(default=0)
    buyer_name = models.CharField(max_length=200)
    buyer_inn = models.CharField(max_length=12, default='0000000000')
    tax_system = models.CharField(max_length=1, default='0')
    send_check_to = models.CharField(max_length=50)
    cash = models.IntegerField()
    ecash = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='Добавлен')

    class Meta:
        verbose_name_plural = 'kkts'

    def __str__(self):
        """Возвращает строковое представление чека."""
        return f"смена {str(self.shft_num)}_чек {str(self.check_num)}"


class Check_good(models.Model):
    """продажи в чек пользователя на ККТ"""
    check_kkt = models.ForeignKey(Check_kkt, on_delete=models.CASCADE, related_name='checkkktset')
    product_name = models.CharField(max_length=200)
    qty = models.IntegerField(default=1)
    tax_code = models.IntegerField(default=6)
    price = models.IntegerField()
    product_type_code = models.IntegerField(default=1)



    def __str__(self):
        """Возвращает строковое представление товара."""
        summa = (self.qty * self.price) / 1000000
        return f"{self.product_name[:50]} на сумму {str(summa)}0"