from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import ATR
from surmount.logging import log
from surmount.data import OHLCV

class FibonacciTradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["AAPL", "GOOGL", "MSFT", "AMZN"]  # List of assets
        self.data_list = [OHLCV(ticker) for ticker in self.tickers]  # Data source for each asset
        self.fibonacci_levels = [0.236, 0.382, 0.5, 0.618, 0.786]  # Fibonacci retracement levels
        self.atr_multiplier = 1.5  # Multiplier for ATR stop-loss
        self.risk_reward_ratio = 2.0  # Desired risk-reward ratio

    @property
    def interval(self):
        return "1day"  # Trading interval

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def calculate_fibonacci_levels(self, high, low):
        """
        Calculate Fibonacci retracement levels.

        :param high: Highest price
        :param low: Lowest price
        :return: List of Fibonacci levels
        """
        price_range = high - low
        return [low + price_range * level for level in self.fibonacci_levels]

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocations
        for ticker in self.tickers:
            ohlcv_data = data.get(("ohlcv", ticker))
            if not ohlcv_data or len(ohlcv_data) < 100:
                continue  # Skip if there isn't enough data

            high = max([row["high"] for row in ohlcv_data[-100:]])
            low = min([row["low"] for row in ohlcv_data[-100:]])
            fib_levels = self.calculate_fibonacci_levels(high, low)

            atr = ATR(ticker, ohlcv_data, 14)  # Calculate ATR
            if atr is None:
                continue

            current_price = ohlcv_data[-1]["close"]

            # Check if price is between 50% and 61.8% Fibonacci levels
            if fib_levels[2] < current_price < fib_levels[3]:
                entry_price = current_price
                stop_loss = entry_price - atr * self.atr_multiplier
                take_profit = entry_price + (entry_price - stop_loss) * self.risk_reward_ratio

                # Log entry details
                log(f"{ticker}: Entry Price = {entry_price}, Stop Loss = {stop_loss}, Take Profit = {take_profit}")

                # Allocate funds to the asset
                allocation_dict[ticker] = 1 / len(self.tickers)

        return TargetAllocation(allocation_dict)