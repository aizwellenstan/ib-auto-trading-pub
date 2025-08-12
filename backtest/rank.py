import yfinance as yf
import numpy as np
import pandas as pd

# Define the stocks
stocks = ['AAPL', 'NVDA', 'TSLA']

# Download stock data
data = yf.download(stocks, start="2020-01-01", end="2023-06-27")

# Define the calculations
def calculate_rank(df):
    # Calculate ts_sum(close, 7)
    ts_sum_close_7 = df['Close'].rolling(window=7).sum()
    
    # Calculate (ts_sum(close, 7) / 7) - close
    mean_close_7 = ts_sum_close_7 / 7
    diff_mean_close = mean_close_7 - df['Close']
    
    # Scale the result
    scaled_diff_mean_close = (diff_mean_close - diff_mean_close.mean()) / diff_mean_close.std()

    # Calculate the correlation between vwap and ts_delay(close, 5)
    vwap = (df['Close'] * df['Volume']).rolling(window=5).sum() / df['Volume'].rolling(window=5).sum()
    ts_delay_close_5 = df['Close'].shift(5)
    correlation = vwap.rolling(window=230).corr(ts_delay_close_5)
    
    # Scale the correlation
    scaled_correlation = (correlation - correlation.mean()) / correlation.std()

    # Calculate the final rank
    rank = scaled_diff_mean_close + (20 * scaled_correlation)
    return rank

# Apply the function to each stock
ranks = {stock: calculate_rank(data[stock]) for stock in stocks}

# Display the results
for stock, rank in ranks.items():
    print(f"Rank for {stock}:\n", rank.dropna().tail())
