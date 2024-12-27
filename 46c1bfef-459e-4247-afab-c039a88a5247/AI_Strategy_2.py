from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Assuming 'new_companies' is a dynamically updated list of ticker symbols
        # that classify as 'new' under certain criteria, possibly updated through external analysis.
        self.new_companies = ["NEWC1", "NEWC2", "NEWC3"]  # Placeholder tickers

    @property
    def assets(self):
        # Assets to potentially trade - new companies list can be dynamically updated
        return self.new_companies

    @property
    def interval(self):
        # Define the interval at which this strategy runs, e.g., daily
        return "1day"

    def run(self, data):
        # Basic logic: Allocate equally among all new companies without further analysis
        # This is a starting point; a real strategy would involve more nuanced decision-making,
        # possibly based on other data like volume, price trends, or fundamental analysis.
        
        # Check if we have at least one new company to invest in
        if len(self.new_companies) > 0:
            allocation_dict = {ticker: 1.0 / len(self.new_companies) for ticker in self.new_companies}
        else:
            log("No new companies to invest in")
            return TargetAllocation({})  # Empty allocation if no new companies
        
        return TargetAllocation(allocation_dict)