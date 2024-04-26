# Simple Trading System

Simple Trading System app implemented with Django Rest Framework. Allows authenticated users the ability to place orders to buy and sell stocks. Also track the over all value of their investments.

## Features

- Place orders: Users can place orders to buy or sell stocks via API through JSON request or CSV file.
- View Order History: Users can view their successfully placed orders.
- Calculate total investment: Users can fetch the total value of their investments in a single stock.

## Limitations
- Partial posting of trades in CSV: If a specific sell order in CSV format exceeds current owned stock, that sell order and all other orders (be it buy or sell) after that row will not be posted. Only valid buy/sell orders prior to it will.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/trading-app.git
   ```

2. Navigate to the project directory:

   ```bash
   cd trading-app
   ```

3. Create a virtual environment and activate it:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run database migrations:

   ```bash
   python manage.py migrate
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

7. Access the app at [http://localhost:8000](http://localhost:8000) in your web browser.

## API Endpoints

Navigate to endpoints for more info.

- `/api/stocks/`: CRUD operations for stocks.
- `/api/user/orders/`: View current user's orders.
- `/api/user/orders/total/?stock_id=<stock_id>`: Calculate total investment in a single stock.
- `/api/trade/`: Place trades to buy or sell stocks.
