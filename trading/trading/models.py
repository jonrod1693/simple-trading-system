from django.db import models
from django.contrib.auth.models import User

from enum import IntEnum


class Stock(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.price}"

    def __repr__(self):
        return str(self.id)


class OrderType(IntEnum):
    BUY = 1
    SELL = -1

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    is_buy_or_sell = models.IntegerField(
        choices=OrderType.choices(), default=OrderType.BUY
    )
    placed_at = models.DateTimeField(auto_now_add=True)

    def get_order_type(self):
        return OrderType(self.is_buy_or_sell).name.title()

    def __str__(self):
        return f"{self.user.get_username()} - {self.stock.name} - {OrderType(self.is_buy_or_sell).name}: {self.stock.price * self.quantity}"

    def value(self):
        return self.quantity * self.stock.price * self.is_buy_or_sell
