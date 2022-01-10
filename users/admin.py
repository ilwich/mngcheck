from django.contrib import admin
from .models import Profile

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'legal_entity', 'personal_acc', 'bank_name', 'bic', 'corres_acc']

admin.site.register(Profile, ProfileAdmin)
