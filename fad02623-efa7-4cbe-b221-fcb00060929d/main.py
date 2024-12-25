import pandas as pd
import numpy as np
from datetime import datetime

class TradingStrategy:
    def __init__(self, data, rsi_period=14, macd_fast=12, macd_slow=26, macd_signal=9, ema_period=200):
        """
        Initialize strategy with OHLCV DataFrame and indicator parameters
        
        Parameters:
        data (DataFrame): OHLCV data with columns ['Open', 'High', 'Low', 'Close', 'Volume']
        """
        self.data = data.copy()
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.ema_period = ema_period
        
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, prices):
        """Calculate MACD and Signal line"""
        exp1 = prices.ewm(span=self.macd_fast).mean()
        exp2 = prices.ewm(span=self.macd_slow).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.macd_signal).mean()
        return macd, signal
    
    def calculate_indicators(self):
        """Calculate all technical indicators"""
        # Calculate RSI
        self.data['RSI'] = self.calculate_rsi(self.data['Close'], self.rsi_period)
        
        # Calculate MACD
        self.data['MACD'], self.data['MACD_Signal'] = self.calculate_macd(self.data['Close'])
        
        # Calculate EMA
        self.data['EMA_200'] = self.data['Close'].ewm(span=self.ema_period).mean()
        
        # Calculate ATR
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
        """Generate trading signals"""
        self.calculate_indicators()
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
    
    def run_backtest(self, initial_capital=10000, risk_percent=0.02):
        """Run backtest with initial capital and risk percentage"""
        self.generate_signals()
        
        # Initialize portfolio metrics
        self.data['Position'] = self.data['Signal'].shift()
        self.data['Returns'] = self.data['Close'].pct_change()
        self.data['Strategy_Returns'] = self.data['Position'] * self.data['Returns']
        
        # Calculate position sizes
        risk_amount = initial_capital * risk_percent
        self.data['Position_Size'] = risk_amount / self.data['ATR']
        
        # Calculate equity curve
        self.data['Equity'] = initial_capital * (1 + self.data['Strategy_Returns']).cumprod()
        
        # Calculate metrics
        total_return = (self.data['Equity'].iloc[-1] / initial_capital - 1)
        sharpe_ratio = np.sqrt(252) * (self.data['Strategy_Returns'].mean() / 
                                      self.data['Strategy_Returns'].std())
        max_drawdown = self.calculate_max_drawdown()
        
        return {
            'Total Return': f"{total_return:.2%}",
            'Sharpe Ratio': f"{sharpe_ratio:.2f}",
            'Max Drawdown': f"{max_drawdown:.2%}",
            'Final Equity': f"{self.data['Equity'].iloc[-1]:.2f}"
        }
    
    def calculate_max_drawdown(self):
        """Calculate maximum drawdown"""
        equity = self.data['Equity']
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        return drawdown.min()
    
    def get_current_signals(self):
        """Get latest indicator values and signals"""
        latest = self.data.iloc[-1]
        return {
            'RSI': f"{latest['RSI']:.2f}",
            'MACD': f"{latest['MACD']:.2f}",
            'MACD Signal': f"{latest['MACD_Signal']:.2f}",
            'EMA 200': f"{latest['EMA_200']:.2f}",
            'Current Signal': 'Buy' if latest['Signal'] == 1 else 'Sell' if latest['Signal'] == -1 else 'Hold'
        }