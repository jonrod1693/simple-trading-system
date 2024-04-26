import csv
import io

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from trading.models import Order, Stock
from trading.serializers import OrderSerializer, StockSerializer, TradeSerializer


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class UserOrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def total(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        stock_id = request.query_params.get("stock_id")
        if not stock_id:
            return Response(
                {"error": "stock_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            orders = queryset.filter(stock_id=stock_id)
            total = sum(order.value() for order in orders)
            return Response(
                {"stock_id": stock_id, "total": total}, status=status.HTTP_200_OK
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Orders not found"}, status=status.HTTP_404_NOT_FOUND
            )


class TradeAPIView(APIView):
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    serializer_class = TradeSerializer

    def post(self, request, format=None):
        if "csv" in request.FILES:
            trades = self.parse_csv(request.FILES["csv"])
            serializer = self.serializer_class(
                data=trades, many=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                # Validate sell orders so user can not sell more than owned stock.
                is_sell_order = serializer.validated_data.get("is_buy_or_sell") == -1
                if is_sell_order:
                    stock_id = serializer.validated_data.get("stock").id
                    quantity = serializer.validated_data.get("quantity")
                    stock_price = Stock.objects.get(pk=stock_id).price
                    selling_value = stock_price * quantity * is_sell_order

                    user_owned_orders = Order.objects.filter(
                        user=request.user, stock_id=stock_id
                    )
                    user_owned_orders_total_value = sum(
                        order.value() for order in user_owned_orders
                    )

                    if (
                        user_owned_orders_total_value is not None
                        and selling_value > user_owned_orders_total_value
                    ):
                        return Response(
                            {
                                "error": f"Unable to sell more than owned stock. Selling: {selling_value}, Owned: {user_owned_orders_total_value}"
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def parse_csv(self, csv_file):
        trades = []
        with io.TextIOWrapper(csv_file, encoding="utf-8", newline="\n") as file:
            reader = csv.DictReader(file)
            for line in reader:
                stock_id = int(line["stock_id"])
                quantity = int(line["quantity"])
                is_buy_or_sell = int(line["is_buy_or_sell"])
                trades.append(
                    {
                        "stock": stock_id,
                        "quantity": quantity,
                        "is_buy_or_sell": is_buy_or_sell,
                    }
                )
        return trades
