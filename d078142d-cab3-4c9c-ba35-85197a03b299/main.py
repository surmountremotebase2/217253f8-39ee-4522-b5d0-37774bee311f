from surmount.base_class import Strategy
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict

class TradingStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.positions: Dict = {}
        self.trade_history: List = []
        self.risk_per_trade = 0.02
        
    def calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate 20 and 200 day moving averages."""
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        return df
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI and MACD."""
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        return df
    
    def check_volume_confirmation(self, df: pd.DataFrame, index: int) -> bool:
        """Check if volume is 20% above average."""
        avg_volume = df['Volume'].rolling(window=20).mean().iloc[index]
        return df['Volume'].iloc[index] > avg_volume * 1.2
    
    def calculate_position_size(self, capital: float, entry: float, stop: float) -> float:
        """Calculate position size based on risk."""
        risk_amount = capital * self.risk_per_trade
        position_size = risk_amount / abs(entry - stop)
        return position_size
    
    def check_entry_signals(self, df: pd.DataFrame, index: int) -> Tuple[bool, str]:
        """Check for entry signals."""
        if index < 200:  # Need enough data for moving averages
            return False, ""
            
        current_data = df.iloc[index]
        prev_data = df.iloc[index-1]
        
        # Trend following entry conditions
        trend_up = (current_data['MA20'] > current_data['MA200'] and 
                   prev_data['MA20'] <= prev_data['MA200'])
        trend_down = (current_data['MA20'] < current_data['MA200'] and 
                     prev_data['MA20'] >= prev_data['MA200'])
        
        # RSI conditions
        rsi_buy = current_data['RSI'] < 30
        rsi_sell = current_data['RSI'] > 70
        
        # Volume confirmation
        volume_confirmed = self.check_volume_confirmation(df, index)
        
        if trend_up and rsi_buy and volume_confirmed:
            return True, "LONG"
        elif trend_down and rsi_sell and volume_confirmed:
            return True, "SHORT"
            
        return False, ""
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        tr = pd.DataFrame()
        tr['h-l'] = df['High'] - df['Low']
        tr['h-pc'] = abs(df['High'] - df['Close'].shift(1))
        tr['l-pc'] = abs(df['Low'] - df['Close'].shift(1))
        tr['tr'] = tr[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        return tr['tr'].rolling(period).mean()

    def trade(self, data: pd.DataFrame) -> List[Dict]:
        """
        Required method for Surmount strategy.
        Returns a list of trades based on the data.
        """
        df = data.copy()
        df = self.calculate_moving_averages(df)
        df = self.calculate_indicators(df)
        df['ATR'] = self.calculate_atr(df)
        
        trades = []
        for i in range(len(df)):
            # Skip if not enough data
            if i < 200:
                continue
                
            signal, direction = self.check_entry_signals(df, i)
            
            if signal:
                entry_price = df['Close'].iloc[i]
                stop_loss = entry_price - (2 * df['ATR'].iloc[i])
                if direction == "SHORT":
                    stop_loss = entry_price + (2 * df['ATR'].iloc[i])
                
                # Calculate position size (assuming $10000 starting capital for this example)
                position_size = self.calculate_position_size(10000, entry_price, stop_loss)
                
                trade = {
                    'date': df.index[i],
                    'action': direction,
                    'price': entry_price,
                    'size': position_size,
                    'stop_loss': stop_loss,
                    'take_profit': entry_price + (abs(entry_price - stop_loss) * 2) if direction == "LONG" else entry_price - (abs(entry_price - stop_loss) * 2)
                }
                trades.append(trade)
        
        return trades