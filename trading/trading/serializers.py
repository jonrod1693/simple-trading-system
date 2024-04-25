from rest_framework import serializers
from .models import Stock, Order

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["name", "price"]

class OrderSerializer(serializers.ModelSerializer):
    value = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ["id", "user", "stock", "quantity", "is_buy_or_sell", "placed_at", "value"]

class TradeSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = Order
        fields = ["id", "stock", "quantity", "is_buy_or_sell", "placed_at", "value"]
