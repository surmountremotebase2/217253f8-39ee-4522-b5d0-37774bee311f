from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, RSI, MACD
from surmount.data import Asset, InstitutionalOwnership, FinancialStatement, InsiderTrading, SocialSentiment, Ratios, GDPALLCountries
from surmount.logging import log


class TradingStrategy(Strategy):
    def __init__(self):
        # Define a mix of tickers across different asset classes for diversification
        self.tickers = ["SPY", "QQQ", "TLT", "GLD", "AAPL", "GOOGL"]
        self.data_list = [InstitutionalOwnership(ticker) for ticker in self.tickers] + \
                         [FinancialStatement(ticker) for ticker in self.tickers] + \
                         [InsiderTrading(ticker) for ticker in self.tickers] + \
                         [SocialSentiment(ticker) for ticker in self.tickers] + \
                         [Ratios(ticker) for ticker in self.tickers] + \
                         [GDPALLCountries()]

    @property
    def interval(self):
        # Daily interval to capture long-term trends and reduce transaction costs
        return "1day"

    @property
    def assets(self):
        return self.tickers

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        allocation_dict = {}
        try:
            for ticker in self.tickers:
                # Example of dynamic allocation based on technical indicators and sentiment analysis
                ema_short = EMA(ticker, data, length=50)
                ema_long = EMA(ticker, data, length=200)
                rsi = RSI(ticker, data, length=14)
                macd = MACD(ticker, data, fast=12, slow=26)
                sentiment = data[("social_sentiment", ticker)]

                # Logic for allocation based on combined indicators and sentiment analysis
                if ema_short[-1] > ema_long[-1] and rsi[-1] < 30 and macd["MACD"][-1] > macd["signal"][-1] and sentiment[-1]["twitterSentiment"] > 0.6:
                    allocation_dict[ticker] = 0.2  # Aggressive allocation
                elif ema_short[-1] < ema_long[-1] or rsi[-1] > 70:
                    allocation_dict[ticker] = 0.05  # Defensive allocation
                else:
                    allocation_dict[ticker] = 0.1  # Neutral allocation

            # Normalize allocations to ensure they sum to 1
            allocation_sum = sum(allocation_dict.values())
            allocation_dict = {ticker: alloc / allocation_sum for ticker, alloc in allocation_dict.items()}
        except Exception as e:
            log(f"Error in strategy execution: {e}")
            allocation_dict = {ticker: 1.0 / len(self.tickers) for ticker in self.tickers}  # Equal allocation as a fallback

        return TargetAllocation(allocation_dict)