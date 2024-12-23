import numpy as np
import pandas as pd

# Optimized Fibonacci Trading Strategy

# Function to calculate Fibonacci retracement levels
def calculate_fibonacci_levels(high_price, low_price, levels):
    price_range = high_price - low_price
    return [low_price + price_range * level for level in levels]

# Function to calculate ATR (Average True Range)
def calculate_atr(data, period=14):
    high_low = data['High'] - data['Low']
    high_close = abs(data['High'] - data['Close'].shift(1))
    low_close = abs(data['Low'] - data['Close'].shift(1))
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

# Configurable inputs
lookback_length = 100  # Lookback period for highs and lows
fibonacci_levels = [0.236, 0.382, 0.5, 0.618, 0.786]  # Fibonacci levels
risk_reward_ratio = 2.0  # Desired risk/reward ratio
atr_multiplier = 1.5  # ATR multiplier for stop loss

# Load historical data (replace with your data source)
# Example: Data should have columns: 'Open', 'High', 'Low', 'Close', 'Volume'
data = pd.read_csv("historical_data.csv")  # Replace with your dataset

# Calculate highs and lows over the lookback period
data['High_Lookback'] = data['High'].rolling(window=lookback_length).max()
data['Low_Lookback'] = data['Low'].rolling(window=lookback_length).min()

# Calculate Fibonacci retracement levels
data['Fibonacci_Levels'] = data.apply(
    lambda row: calculate_fibonacci_levels(row['High_Lookback'], row['Low_Lookback'], fibonacci_levels)
    if not np.isnan(row['High_Lookback']) and not np.isnan(row['Low_Lookback']) else None,
    axis=1
)

# Calculate ATR
data['ATR'] = calculate_atr(data)

# Identify trade opportunities
entries = []
for index, row in data.iterrows():
    if isinstance(row['Fibonacci_Levels'], list) and len(row['Fibonacci_Levels']) > 2:
        fib_50 = row['Fibonacci_Levels'][2]
        fib_61_8 = row['Fibonacci_Levels'][3]
        if row['Close'] > fib_50 and row['Close'] < fib_61_8:
            entry_price = row['Close']
            stop_loss = entry_price - row['ATR'] * atr_multiplier
            take_profit = entry_price + (entry_price - stop_loss) * risk_reward_ratio
            entries.append({'Date': row['Date'], 'Entry': entry_price, 'Stop_Loss': stop_loss, 'Take_Profit': take_profit})

# Convert trade signals into a DataFrame for review
trades = pd.DataFrame(entries)

# Save results
trades.to_csv("optimized_trading_signals.csv", index=False)