import yfinance as yf
import pandas as pd
import numpy as np
import talib as ta
import matplotlib.pyplot as plt

# Fetch historical data from Yahoo Finance
def fetch_data(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date)
    return df

# Calculate MACD and its signal line
def add_macd(df):
    df['MACD'], df['MACD_signal'], _ = ta.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    return df

# Calculate Fibonacci retracement levels
def calculate_fibonacci(df):
    max_price = df['High'].max()
    min_price = df['Low'].min()
    diff = max_price - min_price
    fib_levels = {
        'Level_0': max_price,
        'Level_23.6': max_price - 0.236 * diff,
        'Level_38.2': max_price - 0.382 * diff,
        'Level_50': max_price - 0.5 * diff,
        'Level_61.8': max_price - 0.618 * diff,
        'Level_100': min_price
    }
    return fib_levels

# Volume strategy: Check for breakout confirmation
def volume_breakout(df, threshold=1.5):
    avg_vol = df['Volume'].rolling(window=20).mean()
    breakout_vol = df['Volume'] > (avg_vol * threshold)
    return breakout_vol

# Risk management: Implement stop-loss and take-profit
def risk_management(df, stop_loss_pct=0.02, take_profit_pct=0.05):
    df['Stop_loss'] = df['Close'] * (1 - stop_loss_pct)
    df['Take_profit'] = df['Close'] * (1 + take_profit_pct)
    return df

# Trading signal logic with refined parameters
def trading_signals(df):
    df['Signal'] = 0  # Default signal (no trade)
    
    # Long signal (Buy) when MACD crosses above MACD Signal line, and price is near a key Fibonacci level
    df.loc[(df['MACD'] > df['MACD_signal']) & (df['Close'] > df['Level_50']) & volume_breakout(df), 'Signal'] = 1
    
    # Short signal (Sell) when MACD crosses below MACD Signal line, and price is near a key Fibonacci level
    df.loc[(df['MACD'] < df['MACD_signal']) & (df['Close'] < df['Level_50']) & volume_breakout(df), 'Signal'] = -1
    
    return df

# Backtesting strategy with risk management
def backtest(df, stop_loss_pct=0.02, take_profit_pct=0.05):
    df['Returns'] = df['Close'].pct_change()
    df['Strategy_returns'] = df['Signal'].shift(1) * df['Returns']
    
    # Apply stop-loss and take-profit
    df = risk_management(df, stop_loss_pct, take_profit_pct)
    
    # Apply stop-loss and take-profit logic
    df['Strategy_returns'] = np.where(df['Signal'] == 1, 
                                      np.where(df['Close'] <= df['Stop_loss'], -stop_loss_pct, 
                                               np.where(df['Close'] >= df['Take_profit'], take_profit_pct, df['Strategy_returns'])),
                                      df['Strategy_returns'])
    
    # Calculate cumulative returns
    df['Cumulative_returns'] = (1 + df['Returns']).cumprod() - 1
    df['Cumulative_strategy_returns'] = (1 + df['Strategy_returns']).cumprod() - 1
    
    return df

# Visualize strategy performance
def plot_performance(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df['Cumulative_returns'], label='Buy and Hold', color='blue')
    plt.plot(df['Cumulative_strategy_returns'], label='Strategy', color='red')
    plt.legend()
    plt.title('Strategy vs Buy and Hold')
    plt.show()

# Main function to execute the strategy
def run_strategy(ticker, start_date, end_date):
    # Fetch the data
    df = fetch_data(ticker, start_date, end_date)
    
    # Add technical indicators and Fibonacci retracement
    df = add_macd(df)
    fib_levels = calculate_fibonacci(df)
    for level, price in fib_levels.items():
        df[level] = price

    # Generate trading signals
    df = trading_signals(df)
    
    # Backtest the strategy
    df = backtest(df)
    
    # Plot performance
    plot_performance(df)
    
    return df

# Example: Run the strategy for Apple (AAPL) from 2010 to 2020
df = run_strategy('AAPL', '2010-01-01', '2020-01-01')