from rest_framework import serializers
from .models import SpendingMoney

class SpendingMoneySerializer(serializers.ModelSerializer):
    total_cost = serializers.ReadOnlyField()

    class Meta:
        model = SpendingMoney
        fields = "__all__"
