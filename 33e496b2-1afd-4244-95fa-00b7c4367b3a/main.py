from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, EMA, SMA, MACD, MFI, BB
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        # Define assets to trade. A diversified portfolio can reduce risk.
        self.tickers = ["SPY", "QQQ", "AAPL", "TSLA", "GLD"]
        # Moving Averages for trend analysis
        self.indicators = [SMA(i, 20) for i in self.tickers] + [EMA(i, 50) for i in self.tickers]

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        # Data needed for indicators
        return self.indicators

    def run(self, data):
        allocation_dict = {}
        try:
            for ticker in self.tickers:
                # Moving averages
                short_ma = SMA(ticker, data["ohlcv"], 20)
                long_ma = EMA(ticker, data["ohlcv"], 50)
                
                # Simple strategy: Buy if short-term MA is above long-term MA, indicating an uptrend
                if short_ma[-1] > long_ma[-1]:
                    allocation_dict[ticker] = 1.0 / len(self.tickers)  # Divide capital equally
                else:
                    allocation_dict[ticker] = 0  # Stay out of the market
                
                # Implement stop loss or any other risk management procedure here
                
        except Exception as e:
            log(f"Error in strategy calculation: {e}")
            
        # Ensure target allocation sums up to 1 or less
        allocation = TargetAllocation(allocation_dict)
        return allocation.correct()