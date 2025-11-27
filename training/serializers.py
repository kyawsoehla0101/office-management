from rest_framework import serializers
from .models import TrainingSpendingMoney

class TrainingSpendingMoneySerializer(serializers.ModelSerializer):
    total_cost = serializers.ReadOnlyField()

    class Meta:
        model = TrainingSpendingMoney
        fields = "__all__"
