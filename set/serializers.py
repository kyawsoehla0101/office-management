from rest_framework import serializers
from .models import SoftwareSpendingMoney

class SoftwareSpendingMoneySerializer(serializers.ModelSerializer):
    total_cost = serializers.ReadOnlyField()

    class Meta:
        model = SoftwareSpendingMoney
        fields = "__all__"
