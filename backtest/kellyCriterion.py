import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
from scipy.integrate import quad
from scipy.stats import norm
import yfinance as yf

# Fetch GSPC data
ticker = "^GSPC"
start_date = "2020-03-18"
end_date = "2023-10-22"
data = yf.download(ticker, start=start_date, end=end_date)

# Use the 'Close' prices for returns
closeArr = data['Close'].values

# Calculate returns
returns = np.diff(closeArr) / closeArr[:-1]  # Percentage change
returns = returns[~np.isnan(returns)]  # Remove NaN if any

# Calculate mean and standard deviation
mean_return = np.mean(returns)
std_return = np.std(returns)

def norm_integral(f, mean, std):
    val, er = quad(
        lambda s: np.log(1 + f * s) * norm.pdf(s, mean, std),
        mean - 3 * std,
        mean + 3 * std,
    )
    return -val

def get_kelly(mean, std):
    solution = minimize_scalar(
        norm_integral, 
        args=(mean, std),
        bounds=[0, 2],
        method="bounded"
    )
    return min(solution.x, 1.0)  # Cap the Kelly fraction at 100%

# Calculate Kelly fraction
kelly_fraction = get_kelly(mean_return, std_return)
print(f"Kelly Fraction: {kelly_fraction}")

# Backtesting performance
initial_investment = 1000
investment_values_no_kelly = [initial_investment]
investment_values_kelly = [initial_investment]

# Backtest over the actual returns
for daily_return in returns:
    # Performance without Kelly
    new_value_no_kelly = investment_values_no_kelly[-1] * (1 + daily_return)
    investment_values_no_kelly.append(new_value_no_kelly)

    # Performance with Kelly
    kelly_investment = kelly_fraction * investment_values_kelly[-1]
    new_value_kelly = investment_values_kelly[-1] + kelly_investment * daily_return
    investment_values_kelly.append(new_value_kelly)

# Plot the results
plt.figure(figsize=(12, 6))
plt.plot(investment_values_no_kelly, label='Performance without Kelly', alpha=0.6)
plt.plot(investment_values_kelly, label='Performance with Kelly', alpha=0.6)
plt.title('Investment Performance: With and Without Kelly Criterion on GSPC')
plt.xlabel('Days')
plt.ylabel('Final Investment Value')
plt.legend()
plt.grid()
plt.show()
