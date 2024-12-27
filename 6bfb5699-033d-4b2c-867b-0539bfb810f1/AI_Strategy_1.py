from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD, EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL"]  # Example ticker

    @property
    def interval(self):
        return "1day"  # Daily interval for indicators

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        for ticker in self.tickers:
            try:
                rsi = RSI(ticker, data["ohlcv"], 14)[-1]  # 14-day RSI
                macd_signal = MACD(ticker, data["ohlcv"], 12, 26)["signal"][-1]
                macd_hist = MACD(ticker, data["ohlcv"], 12, 26)["histogram"][-1]
                ema200 = EMA(ticker, data["ohlcv"], 200)[-1]  # 200-period EMA
                last_price = data["ohlcv"][-1][ticker]["close"]

                # Long Entry Condition: RSI < 30, MACD histogram positive (cross up), Price above 200 EMA
                if rsi < 30 and macd_hist > 0 and last_price > ema200:
                    allocation_dict[ticker] = 1.0  # Full allocation
                # Short Entry Condition: Not implemented, as Surmount handles allocations between 0 and 1.
                else:
                    allocation_dict[ticker] = 0  # No allocation, staying out

            except Exception as e:
                log(f"Error processing {ticker}: {e}")
                allocation_dict[ticker] = 0  # Default to no allocation in case of error

        return TargetAllocation(allocation_dict)