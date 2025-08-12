import yfinance as yf
import pandas as pd

# Define the ticker and download intraday data
ticker = "SPY"  # Example ticker, you can change it to any other
data = yf.download(ticker, period="60d", interval="30m")  # Download 7 days of 30-minute interval data

# Ensure the data has no missing values by forward filling
data.ffill(inplace=True)

# Add Date and Time columns for easier manipulation
data['Date'] = data.index.date
data['Time'] = data.index.time

# Calculate the returns for each 30-minute interval
data['Return'] = data['Close'].pct_change()

# Filter out only the last 30-minute interval of each day
last_30min_returns = data.groupby('Date').tail(1)['Return']

# Calculate the cumulative product of the returns
cumulative_product = (last_30min_returns+1).cumprod()

print(cumulative_product)
