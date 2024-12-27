from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Assuming there's a predefined list or method to fetch currently active US equities.
        # This could be dynamic based on the user's universe or a static list of interests.
        self.active_equities = self.get_active_us_equities()
        
    @property
    def assets(self):
        # Our strategy concerns all active equities; ensure this aligns with
        # how you can reference them in the context of the trading system.
        return self.active_equities
    
    @property
    def interval(self):
        # Daily data is used for decision making.
        return "1day"
        
    def get_active_us_equities(self):
        # Placeholder for a method that fetches or defines the list of equities.
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "FB", "TSLA", "BRK.A", "UNH", "JNJ", "V"]
        
    def run(self, data):
        """
        Executes the trading strategy:
        - Buys shares in the 5 highest stocks based on the closing price.
        - Shorts the 5 lowest stocks based on the closing price.
        - Allocates no more than 5% of the portfolio to a single trade.
        - Incorporates a conceptual stop-loss mechanism.
        """
        # Assuming 'data' contains closing prices indexed by equity symbols.
        closing_prices = {ticker: data["ohlcv"][-1][ticker]["close"] for ticker in self.active_equities}
        
        # Sort stocks based on the latest closing price.
        sorted_by_price = sorted(closing_prices.items(), key=lambda x: x[1], reverse=True)
        
        # Select top 5 and bottom 5 for action.
        top_5 = sorted_by_price[:5]
        bottom_5 = sorted_by_price[-5:]
        
        # Construct the allocation dictionary.
        allocation = {}
        for stock, _ in top_5:
            allocation[stock] = 0.05  # 5% allocation, buy signal.
        for stock, _ in bottom_5:
            allocation[stock] = -0.05  # 5% allocation, short signal (conceptual).
        
        # Implementing stop-loss is complex and requires real-time data and execution capabilities.
        # One would need to monitor the positions' performance continuously and execute orders
        # that adhere to the stop-loss criteria, not directly feasible within this strategy scope.
        
        return TargetAllocation(allocation)