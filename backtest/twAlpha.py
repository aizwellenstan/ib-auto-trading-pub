import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from modules.sharpe import get_annualized_return, get_sharpe_ratio, get_mdd

start_date = '2007-01-01'
end_date = '2024-05-27'
tickers = ['00713.TW', 'IBIT']

data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']

returns = data.pct_change().dropna()
"""
6m rebalance

1張 00713 $58000
5lot 2330 $40000
1lot 小台 $46000
--------------------

6, 7, 8 小台近遠月套利
"""
returns['Strategy'] = (returns['00713.TW'] + returns['2330.TW']*0.5122 - returns['0050.TW']) # 金融期 電子期?

cumulative_returns = (returns['Strategy'] + 1).cumprod()

ar = get_annualized_return(cumulative_returns)
sr = get_sharpe_ratio(cumulative_returns)
mdd = get_mdd(cumulative_returns)
print("AR: ", ar)
print("SR: ", sr)
print("MDD: ", mdd)

plt.figure(figsize=(10, 6))
cumulative_returns.plot(title='00713+2330 Alpha')
plt.xlabel('Date')
plt.ylabel('Cumulative Returns')
plt.grid(True)
plt.show()
