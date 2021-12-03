from django.contrib import admin

# Register your models here.
from .models import Kkt, Check_kkt, Check_good

admin.site.register(Kkt)
admin.site.register(Check_kkt)
admin.site.register(Check_good)