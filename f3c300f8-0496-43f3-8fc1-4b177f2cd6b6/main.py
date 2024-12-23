from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import Asset, InstitutionalOwnership, InsiderTrading

class TradingStrategy(Strategy):
    def __init__(self):
        # SPY for market sentiment, QQQ for trading asset
        self.tickers = ["SPY", "QQQ"]
        # Fetching data for insider trading and institutional ownership for the market sentiment asset SPY
        self.data_list = [InsiderTrading("SPY"), InstitutionalOwnership("SPY")]

    @property
    def interval(self):
        # Daily observations provide a broad market sentiment outlook
        return "1day"

    @property
    def assets(self):
        # Trading focus on QQQ based on SPY market sentiment
        return ["QQQ"]

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {"QQQ": 0}  # Start with no allocation
        spy_insider_data = data[("insider_trading", "SPY")]
        spy_institutional_data = data[("institutional_ownership", "SPY")]

        # Basic logic: if recent insider sales and institutional ownership trends suggest pessimism, stay out of QQQ
        if spy_insider_data and any(["Sale" in transaction['transactionType'] for transaction in spy_insider_data[-3:]]):
            log("Market sentiment poor based on insider sales; avoiding QQQ")
        elif spy_institutional_data and spy_institutional_data[-1]["ownershipPercentChange"] < 0:
            log("Market sentiment poor based on institutional ownership; avoiding QQQ")
        else:
            # If the market sentiment is not bad, allocate a portion to QQQ
            allocation_dict["QQQ"] = 0.1  # Example allocation, could be dynamic based on strategy sophistication

        return TargetAllocation(allocation_dict)