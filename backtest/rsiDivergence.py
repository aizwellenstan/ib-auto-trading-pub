import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def detect_divergences(prices, rsi, lookback_left=5, lookback_right=5):
    bullish_divergences = []
    bearish_divergences = []
    
    for i in range(lookback_right, len(prices) - lookback_right):
        price_range = prices[i-lookback_left:i+lookback_right+1]
        rsi_range = rsi[i-lookback_left:i+lookback_right+1]
        
        if rsi[i-lookback_right] > np.max(rsi_range[:lookback_left]) and \
           prices[i-lookback_right] < np.min(price_range[:lookback_left]):
            bullish_divergences.append(i)
        
        if rsi[i-lookback_right] < np.min(rsi_range[:lookback_left]) and \
           prices[i-lookback_right] > np.max(price_range[:lookback_left]):
            bearish_divergences.append(i)
    
    return bullish_divergences, bearish_divergences

def plot_rsi_with_divergences(prices, rsi, bullish_divergences, bearish_divergences):
    plt.figure(figsize=(14, 8))

    plt.subplot(2, 1, 1)
    plt.plot(prices, label='Price')
    plt.title('Price')
    
    plt.subplot(2, 1, 2)
    plt.plot(rsi, label='RSI', color='purple')
    plt.axhline(70, color='red', linestyle='--')
    plt.axhline(30, color='green', linestyle='--')
    plt.scatter(bullish_divergences, rsi[bullish_divergences], color='green', marker='^', label='Bullish Divergence')
    plt.scatter(bearish_divergences, rsi[bearish_divergences], color='red', marker='v', label='Bearish Divergence')
    plt.title('RSI with Divergences')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

# Fetch historical data
symbol = 'NVDA'  # Example symbol
data = yf.download(symbol, start='2024-09-01', end='2024-10-01', interval='5m')
prices = data['Close']
rsi = calculate_rsi(prices)

# Detect divergences
bullish_divergences, bearish_divergences = detect_divergences(prices, rsi)

# Plot results
plot_rsi_with_divergences(prices, rsi, bullish_divergences, bearish_divergences)
