from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Order, Stock
from io import StringIO


class UserOrderViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_order_user")
        self.client.force_authenticate(user=self.user)

        self.stock1 = Stock.objects.create(name="Stock 1", price=100)
        self.stock2 = Stock.objects.create(name="Stock 2", price=200)

        Order.objects.create(user=self.user, stock=self.stock1, quantity=10)
        Order.objects.create(user=self.user, stock=self.stock2, quantity=5)

    def test_total(self):
        url = reverse("user-orders-total")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        url = f"{reverse('user-orders-total')}?stock_id={self.stock1.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock_id"], str(self.stock1.id))
        self.assertEqual(response.data["total"], 1000)  # 10 * 100 = 1000

        url = f"{reverse('user-orders-total')}?stock_id={self.stock2.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock_id"], str(self.stock2.id))
        self.assertEqual(response.data["total"], 1000)  # 5 * 200 = 1000

    def test_total_invalid_stock_id(self):
        mock_stock_id = 1000
        url = f"{reverse('user-orders-total')}?stock_id={mock_stock_id}"  # Non-existing stock ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], f"Stock ID: {mock_stock_id} not found")

    def test_no_orders_returns_zero(self):
        Order.objects.all().delete()

        url = f"{reverse('user-orders-total')}?stock_id={self.stock1.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock_id"], str(self.stock1.id))
        self.assertEqual(response.data["total"], 0)

        url = f"{reverse('user-orders-total')}?stock_id={self.stock2.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock_id"], str(self.stock2.id))
        self.assertEqual(response.data["total"], 0)


class TradeAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_trade_user")
        self.client.force_authenticate(user=self.user)

        self.stock = Stock.objects.create(name="Test Stock", price=100)
        self.order = Order.objects.create(user=self.user, stock=self.stock, quantity=10)

    def test_create_trades_from_csv(self):
        # Sample CSV data
        csv_data = "stock_id,quantity,is_buy_or_sell\n\
                    1,5,1\n\
                    1,3,-1\n\
                    1,100,-1\n"
        csv_file = StringIO(csv_data)
        file_upload = SimpleUploadedFile("trades.csv", csv_file.read().encode())

        url = reverse("trade")
        response = self.client.post(url, {"csv": file_upload}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 3)

        buy_order = Order.objects.get(id=2)
        self.assertEqual(buy_order.stock, self.stock)
        self.assertEqual(buy_order.quantity, 5)
        self.assertEqual(buy_order.is_buy_or_sell, 1)

        sell_order = Order.objects.last()
        self.assertEqual(sell_order.stock, self.stock)
        self.assertEqual(sell_order.quantity, 3)
        self.assertEqual(sell_order.is_buy_or_sell, -1)

    def test_valid_buy_trade(self):
        data = {"stock": self.stock.id, "quantity": 5, "is_buy_or_sell": 1}
        url = reverse("trade")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)  # Assuming the trade was successful

    def test_valid_sell_trade(self):
        data = {"stock": self.stock.id, "quantity": 5, "is_buy_or_sell": -1}
        url = reverse("trade")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)  # Assuming the trade was successful

    def test_invalid_sell_trade(self):
        data = {"stock": self.stock.id, "quantity": 20, "is_buy_or_sell": -1}
        url = reverse("trade")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 1)  # No new order should be created
