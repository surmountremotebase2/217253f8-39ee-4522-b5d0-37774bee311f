from surmount.base_class import Strategy, TargetAllocation
from surmount.data import InstitutionalOwnership

class TradingStrategy(Strategy):
    def __init__(self):
        # Specify tickers of interest, can be expanded based on preferences
        self.tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "FB"]
        # Initialize data_list with InstitutionalOwnership objects for each ticker
        self.data_list = [InstitutionalOwnership(ticker) for ticker in self.tickers]

    @property
    def interval(self):
        # Daily checks should be sufficient for this strategy
        return "1day"

    @property
    def assets(self):
        # Return the list of tickers to be monitored
        return self.tickers

    @property
    def data(self):
        # Return the initialized data sources required for this strategy
        return self.data_list

    def run(self, data):
        # Initialize an empty dictionary to hold our target allocations
        allocation_dict = {}

        # Check each data point in our data_list
        for inst_ownership_data in self.data_list:
            ticker = inst_ownership_data.asset.ticker  # Extract the ticker for ease of use
            allocation_dict[ticker] = 0  # Initialize each ticker's allocation to 0
            
            # The data for InstitutionalOwnership should provide details on recent investments
            # Check if Vanguard's latest investment in this asset is at least $500 million
            for investment in data[tuple(inst_ownership_data)]:
                if investment["investor"] == "Vanguard" and investment["amount"] >= 500e6:
                    # If so, set the allocation for this ticker to be a fractional value of the portfolio
                    # This can be adjusted based on risk tolerance and diversification strategy
                    allocation_dict[ticker] = 1/len(self.tickers)  # Equally distribute investment across all tickers meeting criteria
                    
                    # Log the significant investment activity
                    print(f"Vanguard investment in {ticker} meets criteria")

        # Return the calculated target allocations as a TargetAllocation object
        return TargetAllocation(allocation_dict)