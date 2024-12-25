import pandas as pd
import numpy as np
import yfinance as yf
from ta.trend import MACD
from ta.momentum import RSIIndicator
import datetime

class MultiIndicatorStrategy:
    def __init__(self, symbol, start_date, end_date, rsi_period=14, 
                 macd_fast=12, macd_slow=26, macd_signal=9, ema_period=200):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.ema_period = ema_period
        
    def fetch_data(self):
        """Fetch historical data and calculate indicators"""
        self.data = yf.download(self.symbol, self.start_date, self.end_date)
        
        # Calculate RSI
        rsi = RSIIndicator(close=self.data['Close'], window=self.rsi_period)
        self.data['RSI'] = rsi.rsi()
        
        # Calculate MACD
        macd = MACD(close=self.data['Close'], 
                    window_slow=self.macd_slow,
                    window_fast=self.macd_fast,
                    window_sign=self.macd_signal)
        self.data['MACD'] = macd.macd()
        self.data['MACD_Signal'] = macd.macd_signal()
        
        # Calculate EMA
        self.data['EMA_200'] = self.data['Close'].ewm(span=self.ema_period).mean()
        
        # Calculate ATR for position sizing
        self.data['ATR'] = self.calculate_atr(14)
        
    def calculate_atr(self, period):
        """Calculate Average True Range"""
        high = self.data['High']
        low = self.data['Low']
        close = self.data['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    
    def generate_signals(self, rsi_oversold=30, rsi_overbought=70):
        """Generate trading signals based on indicator combinations"""
        self.data['Signal'] = 0
        
        # Long signals
        long_condition = (
            (self.data['RSI'] < rsi_oversold) &  # RSI oversold
            (self.data['MACD'] > self.data['MACD_Signal']) &  # MACD crossover
            (self.data['Close'] > self.data['EMA_200'])  # Price above EMA
        )
        
        # Short signals
        short_condition = (
            (self.data['RSI'] > rsi_overbought) &  # RSI overbought
            (self.data['MACD'] < self.data['MACD_Signal']) &  # MACD crossunder
            (self.data['Close'] < self.data['EMA_200'])  # Price below EMA
        )
        
        self.data.loc[long_condition, 'Signal'] = 1
        self.data.loc[short_condition, 'Signal'] = -1
        
    def calculate_position_size(self, account_size, risk_percent=0.02):
        """Calculate position size based on ATR and risk parameters"""
        risk_amount = account_size * risk_percent
        self.data['Position_Size'] = risk_amount / self.data['ATR']
        
    def backtest(self, initial_capital=100000):
        """Run backtest and calculate performance metrics"""
        self.data['Returns'] = self.data['Close'].pct_change()
        self.data['Strategy_Returns'] = self.data['Signal'].shift() * self.data['Returns']
        
        # Calculate cumulative returns
        self.data['Cumulative_Returns'] = (1 + self.data['Returns']).cumprod()
        self.data['Strategy_Cumulative_Returns'] = (1 + self.data['Strategy_Returns']).cumprod()
        
        # Calculate performance metrics
        total_return = self.data['Strategy_Cumulative_Returns'].iloc[-1] - 1
        sharpe_ratio = np.sqrt(252) * (self.data['Strategy_Returns'].mean() / 
                                      self.data['Strategy_Returns'].std())
        
        return {
            'Total Return': f"{total_return:.2%}",
            'Sharpe Ratio': f"{sharpe_ratio:.2f}",
            'Max Drawdown': f"{self.calculate_max_drawdown():.2%}"
        }
    
    def calculate_max_drawdown(self):
        """Calculate maximum drawdown"""
        cumulative = self.data['Strategy_Cumulative_Returns']
        rolling_max = cumulative.expanding().max()
        drawdowns = cumulative/rolling_max - 1
        return drawdowns.min()
    
    def get_current_signals(self):
        """Get current indicator values and signals"""
        latest = self.data.iloc[-1]
        return {
            'RSI': f"{latest['RSI']:.2f}",
            'MACD': f"{latest['MACD']:.2f}",
            'MACD Signal': f"{latest['MACD_Signal']:.2f}",
            'EMA 200': f"{latest['EMA_200']:.2f}",
            'Current Signal': 'Buy' if latest['Signal'] == 1 else 'Sell' if latest['Signal'] == -1 else 'Hold'
        }

# Example usage
strategy = MultiIndicatorStrategy(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date=datetime.datetime.now()
)

strategy.fetch_data()
strategy.generate_signals()
strategy.calculate_position_size(account_size=100000)

# Get performance metrics
results = strategy.backtest()
current_signals = strategy.get_current_signals()