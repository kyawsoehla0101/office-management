from rest_framework import serializers
from .models import HardwareSpendingMoney

class HardwareSpendingMoneySerializer(serializers.ModelSerializer):
    total_cost = serializers.ReadOnlyField()

    class Meta:
        model = HardwareSpendingMoney
        fields = "__all__"
