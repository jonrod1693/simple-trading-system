from django.urls import path, include
from rest_framework.routers import DefaultRouter
from trading.views import StockViewSet, UserOrderViewSet, TradeAPIView

router = DefaultRouter()
router.register(r"stocks", StockViewSet, basename="stock")
router.register(r"user/orders", UserOrderViewSet, basename="user-orders")


urlpatterns = [
    path("", include(router.urls)),
    path("trade/", TradeAPIView.as_view(), name="trade"),
]
