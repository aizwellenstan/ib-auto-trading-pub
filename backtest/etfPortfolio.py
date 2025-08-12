import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

# Define the tickers for SPY, QQQ, TQQQ, and SOXL
tickers = ["SPY", "QQQ", "TQQQ", "SOXL"]
start_date = "2020-03-18"
end_date = "2024-10-22"

# Fetch data for each ticker
data = {ticker: yf.download(ticker, start=start_date, end=end_date)['Close'] for ticker in tickers}

# Calculate daily returns for each ETF
# returns = {ticker: data[ticker].pct_change().dropna() for ticker in tickers}
returns = {ticker: np.diff(data[ticker]) / data[ticker][:-1] for ticker in tickers}

# Backtesting performance with 50% investment
initial_investment = 1000
investment_values = {ticker: [initial_investment] for ticker in tickers}

# Backtest over the actual returns
for i in range(len(returns["SPY"])):
    for ticker in tickers:
        # 50% of the portfolio is allocated to the ETF
        kelly_investment = 0.5 * investment_values[ticker][-1]
        new_value = investment_values[ticker][-1] + kelly_investment * returns[ticker].iloc[i]
        investment_values[ticker].append(new_value)
for ticker in tickers:
    print(ticker, investment_values[ticker][-1])

import sys
sys.exit()
# Plot the results
plt.figure(figsize=(12, 6))
for ticker in tickers:
    plt.plot(investment_values[ticker], label=f'Performance of {ticker}', alpha=0.6)

plt.title('Investment Performance Comparison: SPY, QQQ, TQQQ, SOXL (50% Allocation)')
plt.xlabel('Days')
plt.ylabel('Final Investment Value')
plt.legend()
plt.grid()
plt.show()
