from surmount.base_class import Strategy, TargetAllocation
from surmount.data import Asset
from surmount.technical_indicators import OBV  # On-Balance Volume for volume trend
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the asset or assets of interest
        self.tickers = ["XYZ"]  # Example ticker; replace with your target asset(s)
        
        # Initialize a dictionary to keep track of entry prices for calculating profits
        self.entry_prices = {ticker: None for ticker in self.tickers}
        
        # Other relevant initialization parameters can be added here
       
    @property
    def assets(self):
        # Specify the list of assets the strategy will work with
        return self.tickers

    @property
    def interval(self):
        # Define the data interval (granularity of data)
        return "1day"  # Using daily data; adjust as needed for more/less frequency
    
    def run(self, data):
        # Initialize allocation with no position
        allocation_dict = {ticker: 0 for ticker in self.tickers}
        
        for ticker in self.tickers:
            ohlcv_data = data["ohlcv"]  # Assuming 'data' is a dict containing OHLCV as one of its keys
            if len(ohlcv_data) < 2:
                continue  # Need at least 2 data points to compare volumes
            
            # Calculate On-Balance Volume (OBV) to consider the volume trend
            obv_values = OBV(ticker, ohlcv_data)
            if obv_values is None or len(obv_values) < 2:
                continue  # Not enough data to calculate OBV or failed calculation
            
            # Entry condition based on the increase of volume indicated by OBV
            if obv_values[-1] > obv_values[-2] * 1.1:  # For example, 10% increase from previous day
                # Set allocation to 1 (full allocation) upon entry condition met
                allocation_dict[ticker] = 1
                self.entry_prices[ticker] = ohlcv_data[-1][ticker]["close"]  # Update entry price
            
            elif self.entry_prices[ticker]:
                # Exit condition based on 20% profit target
                current_price = ohlcv_data[-1][ticker]["close"]
                entry_price = self.entry_prices[ticker]
                if current_price >= entry_price * 1.20:
                    log(f"Exiting {ticker} at {current_price} for a 20% profit.")
                    allocation_dict[ticker] = 0  # Exit position
                    self.entry_prices[ticker] = None  # Reset entry price upon exit

        return TargetAllocation(allocation_dict)