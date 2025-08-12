import numpy as np

def sortino_ratio(returns, risk_free_rate=0):
    downside_returns = returns[returns < 0]
    expected_return = np.mean(returns)
    downside_deviation = np.std(downside_returns)
    if downside_deviation == 0:
        return np.inf  # To avoid division by zero
    sortino_ratio = (expected_return - risk_free_rate) / downside_deviation
    return sortino_ratio

def portfolio_sortino_ratio(close_prices_long, close_prices_short, weight_long=0.5, weight_short=0.5, risk_free_rate=0):
    """
    Calculate Sortino ratio for a portfolio consisting of one long and one short asset.

    Parameters:
    close_prices_long : array-like
        Array of close prices for the long asset.
    close_prices_short : array-like
        Array of close prices for the short asset.
    weight_long : float, optional
        Weight of the long asset in the portfolio (default is 0.5).
    weight_short : float, optional
        Weight of the short asset in the portfolio (default is 0.5).
    risk_free_rate : float, optional
        Annual risk-free rate, default is 0.

    Returns:
    float
        Sortino ratio of the portfolio.
    """
    # Calculate returns from close prices
    returns_long = np.diff(close_prices_long) / close_prices_long[:-1]
    returns_short = np.diff(close_prices_short) / close_prices_short[:-1]

    # Calculate portfolio returns (long + short)
    portfolio_returns = weight_long * returns_long + weight_short * returns_short
    
    # Calculate Sortino Ratio
    
    
    # Calculate Sortino Ratio for the portfolio
    sortino = sortino_ratio(portfolio_returns)
    
    return sortino

# # Example usage:
# close_prices_long = [100, 102, 98, 104, 101]
# close_prices_short = [80, 78, 82, 80, 84]

# sortino_ratio = portfolio_sortino_ratio(close_prices_long, close_prices_short)

