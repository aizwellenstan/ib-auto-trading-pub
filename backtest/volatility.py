import numpy as np

# Example close price data (replace with your own data)
close_prices = np.array([100.0, 102.0, 101.5, 105.0, 103.5])

# Calculate daily returns
returns = np.diff(close_prices) / close_prices[:-1]

print(returns)
# Calculate volatility for day 3
day3_volatility = np.std(returns[:4])

print("Day 3 volatility:", day3_volatility)
