import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# Download the historical data of QQQ and CAT from Yahoo Finance
qqq = yf.Ticker("QQQ").history(period="360d")
print(qqq.iloc[-1])
cat = yf.Ticker("CAT").history(period="360d")

# Define the custom shift period for QQQ stock data (in days)
shift_period = -64

# Shift the QQQ stock data by the custom period
qqq_shifted = qqq.shift(shift_period)

# Combine the CAT and shifted QQQ data into a single DataFrame
data = pd.concat([cat['Close'], qqq_shifted['Close']], axis=1)
data.columns = ['CAT', 'QQQ']

# Find the index of the lowest and highest points in the CAT data
min_index = data['CAT'].idxmin()
max_index = data['CAT'].idxmax()

# Plot the data using matplotlib
fig, ax = plt.subplots(figsize=(20, 10))
ax.plot(data['CAT'], label='CAT')
ax.plot(qqq_shifted['Close'], label='QQQ')
ax.axvline(min_index, color='red', linestyle='--', label='Lowest point')
ax.axvline(max_index, color='green', linestyle='--', label='Highest point')  # new line
ax.set_title('CAT vs QQQ (shifted by {} days)'.format(-shift_period))
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.legend()

# Set the x-axis tick labels to the original date
tick_labels = qqq.index.strftime('%Y-%m-%d').tolist()
ax.set_xticklabels(tick_labels)

plt.show()
