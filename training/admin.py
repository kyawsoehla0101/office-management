from django.contrib import admin
from training.models import TrainingSpendingMoney
from .models import Member as TrainingMember

# Register your models here.
admin.site.register(TrainingSpendingMoney)
admin.site.register(TrainingMember)
