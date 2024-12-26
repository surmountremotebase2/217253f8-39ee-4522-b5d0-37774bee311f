from surmount.base_class import Strategy
import pandas as pd
import numpy as np

class TradingStrategy(Strategy):
    def __init__(self):
        self.rsi_period = 14
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        self.ema_period = 200
        
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
    
    def calculate_atr(self, high, low, close, period=14):
        """Calculate Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def run(self, data):
        """
        Main strategy execution method required by the framework
        """
        # Initialize the positions array
        positions = pd.Series(index=data.index, dtype=float)
        positions.iloc[0] = 0

        # Calculate indicators
        rsi = self.calculate_rsi(data['Close'], self.rsi_period)
        macd, macd_signal = self.calculate_macd(data['Close'])
        ema_200 = data['Close'].ewm(span=self.ema_period).mean()
        atr = self.calculate_atr(data['High'], data['Low'], data['Close'])

        # Generate signals
        for i in range(1, len(data)):
            positions.iloc[i] = 0  # Default position

            # Long signals
            if (rsi.iloc[i-1] < 30 and  # RSI oversold
                macd.iloc[i-1] > macd_signal.iloc[i-1] and  # MACD crossover
                data['Close'].iloc[i-1] > ema_200.iloc[i-1]):  # Price above EMA
                positions.iloc[i] = 1

            # Short signals
            elif (rsi.iloc[i-1] > 70 and  # RSI overbought
                  macd.iloc[i-1] < macd_signal.iloc[i-1] and  # MACD crossunder
                  data['Close'].iloc[i-1] < ema_200.iloc[i-1]):  # Price below EMA
                positions.iloc[i] = -1

        return positions