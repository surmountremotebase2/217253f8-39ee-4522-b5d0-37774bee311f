from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import DataClass  # Replace `OHLCV` with a valid import
from surmount.technical_indicators import ATR  # Keep the ATR import or adjust if necessary

class FibonacciTradingStrategy(Strategy):

    def __init__(self):
        self.tickers = ["AAPL", "GOOGL", "MSFT", "AMZN"]
        self.data_list = [DataClass(ticker) for ticker in self.tickers]  # Replace `DataClass` with the correct data source
        self.fibonacci_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
        self.atr_multiplier = 1.5
        self.risk_reward_ratio = 2.0

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def calculate_fibonacci_levels(self, high, low):
        price_range = high - low
        return [low + price_range * level for level in self.fibonacci_levels]

    def run(self, data):
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        for ticker in self.tickers:
            ticker_data = data.get(("ohlcv", ticker))  # Adjust key as per the available data structure
            if not ticker_data or len(ticker_data) < 100:
                continue

            high = max([row["high"] for row in ticker_data[-100:]])
            low = min([row["low"] for row in ticker_data[-100:]])
            fib_levels = self.calculate_fibonacci_levels(high, low)

            atr = ATR(ticker, ticker_data, 14)
            if atr is None:
                continue

            current_price = ticker_data[-1]["close"]

            if fib_levels[2] < current_price < fib_levels[3]:
                entry_price = current_price
                stop_loss = entry_price - atr * self.atr_multiplier
                take_profit = entry_price + (entry_price - stop_loss) * self.risk_reward_ratio

                log(f"{ticker}: Entry Price = {entry_price}, Stop Loss = {stop_loss}, Take Profit = {take_profit}")
                allocation_dict[ticker] = 1 / len(self.tickers)

        return TargetAllocation(allocation_dict)