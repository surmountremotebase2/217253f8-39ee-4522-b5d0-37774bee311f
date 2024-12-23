from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import InsiderTrading, InstitutionalOwnership, SocialSentiment, Dividend, FinancialStatement, Ratios
from surmount.technical_indicators import ATR  # Keep ATR if needed

class MultiDataStrategy(Strategy):

    def __init__(self):
        self.tickers = ["AAPL", "GOOGL", "MSFT", "AMZN"]
        self.data_list = [
            InsiderTrading("AAPL"),
            InstitutionalOwnership("AAPL"),
            SocialSentiment("AAPL"),
            Dividend("AAPL"),
            FinancialStatement("AAPL"),
            Ratios("AAPL")
        ]
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
            insider_trading_dict = data.get(("insider_trading", ticker))
            institutional_ownership_dict = data.get(("institutional_ownership", ticker))
            social_sentiment_dict = data.get(("social_sentiment", ticker))
            dividend_dict = data.get(("dividend", ticker))
            financial_statement_dict = data.get(("financial_statement", ticker))
            ratios_dict = data.get(("ratios", ticker))
            
            if not ticker_data or len(ticker_data) < 100:
                continue

            # Fibonacci Levels Calculation
            high = max([row["high"] for row in ticker_data[-100:]])
            low = min([row["low"] for row in ticker_data[-100:]])
            fib_levels = self.calculate_fibonacci_levels(high, low)

            # ATR Calculation
            atr = ATR(ticker, ticker_data, 14)
            if atr is None:
                continue

            current_price = ticker_data[-1]["close"]

            # Insider Trading Insights
            insider_data = insider_trading_dict[-1] if insider_trading_dict else None
            if insider_data:
                log(f"{ticker} Insider Trading: {insider_data['transactionType']} on {insider_data['transactionDate']}")

            # Institutional Ownership Insights
            institutional_data = institutional_ownership_dict[-1] if institutional_ownership_dict else None
            if institutional_data:
                log(f"{ticker} Institutional Ownership: {institutional_data['ownershipPercent']}%")

            # Social Sentiment Insights
            social_sentiment = social_sentiment_dict[-1] if social_sentiment_dict else None
            if social_sentiment:
                log(f"{ticker} Social Sentiment: StockTwits Sentiment = {social_sentiment['stocktwitsSentiment']}, Twitter Sentiment = {social_sentiment['twitterSentiment']}")

            # Dividend Insights
            dividend_data = dividend_dict[-1] if dividend_dict else None
            if dividend_data:
                log(f"{ticker} Dividend: {dividend_data['dividend']} on {dividend_data['date']}")

            # Financial Statement Insights
            financial_data = financial_statement_dict[-1] if financial_statement_dict else None
            if financial_data:
                log(f"{ticker} Financials: Revenue = {financial_data['revenue']}")

            # Ratios Insights
            ratios_data = ratios_dict[-1] if ratios_dict else None
            if ratios_data:
                log(f"{ticker} Financial Ratios: Return on Equity = {ratios_data['returnOnEquity']}")

            # Entry and Exit Decision Based on Fibonacci Levels and ATR
            if fib_levels[2] < current_price < fib_levels[3]:
                entry_price = current_price
                stop_loss = entry_price - atr * self.atr_multiplier
                take_profit = entry_price + (entry_price - stop_loss) * self.risk_reward_ratio

                log(f"{ticker}: Entry Price = {entry_price}, Stop Loss = {stop_loss}, Take Profit = {take_profit}")
                allocation_dict[ticker] = 1 / len(self.tickers)

        return TargetAllocation(allocation_dict)