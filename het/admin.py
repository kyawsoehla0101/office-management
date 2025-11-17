from django.contrib import admin

# Register your models here.
from .models import HardwareRepair, HardwareSpendingMoney
from .models import Member as HetMember

admin.site.register(HardwareRepair)
admin.site.register(HardwareSpendingMoney)
admin.site.register(HetMember)
