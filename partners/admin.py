from django.contrib import admin
from .models import Partnerprofile, PaymentCode, Contract, CodeOrder

# Register your models here.

admin.site.register(Partnerprofile)
admin.site.register(Contract)
admin.site.register(PaymentCode)
admin.site.register(CodeOrder)
