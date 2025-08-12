import numpy as np

def rsi_metrics(close, signal, low=30.29, high=78.95):
    # Initialize variables
    position = 0  # 1 for long, -1 for short, 0 for neutral
    start_price = 0
    end_price = 0
    trades = []

    # Iterate over the signals
    for i in range(len(signal)):
        if signal[i] < low and position == 0:  # Buy signal
            position = 1
            start_price = close[i]
        elif signal[i] > high and position == 1:  # Sell signal
            position = 0
            end_price = close[i]
            trades.append((start_price, end_price))

    # Calculate returns
    returns = 0
    for start, end in trades:
        returns += (end - start) / start

    # Calculate Sharpe Ratio
    daily_returns = np.diff(close) / close[:-1]
    sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)

    return returns, sharpe_ratio
    # Calculate Maximum Drawdown (MDD)
    cumulative_returns = np.cumsum(daily_returns)
    high_watermark = np.maximum.accumulate(cumulative_returns)
    drawdown = -99999
    try:
        drawdown = (cumulative_returns - high_watermark) / high_watermark
    except: mdd = -99999
    max_drawdown = np.min(drawdown)
    return returns, sharpe_ratio, max_drawdown
    # Calculate Sortino Ratio
    downside_returns = daily_returns[daily_returns < 0]
    sortino_ratio = np.mean(daily_returns) / np.std(downside_returns) * np.sqrt(252)

    # return returns, sharpe_ratio, max_drawdown, sortino_ratio