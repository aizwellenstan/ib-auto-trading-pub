import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from modules.sharpe import get_annualized_return, get_sharpe_ratio, get_mdd
from modules.aiztradingview import GetDayTrade, GetETF

def Backtest(symbol):
    start_date = '2007-01-01'
    end_date = '2024-05-27'
    tickers = [symbol, 'TSM', 'EWT']

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
    returns['Strategy'] = (returns[symbol] + returns['TSM']*0.5122 - returns['EWT']) # 金融期 電子期?

    cumulative_returns = (returns['Strategy'] + 1).cumprod()

    ar = get_annualized_return(cumulative_returns)
    sr = get_sharpe_ratio(cumulative_returns)
    mdd = get_mdd(cumulative_returns)
    # print("AR: ", ar)
    # print("SR: ", sr)
    # print("MDD: ", mdd)

    # plt.figure(figsize=(10, 6))
    # cumulative_returns.plot(title='00713+2330 Alpha')
    # plt.xlabel('Date')
    # plt.ylabel('Cumulative Returns')
    # plt.grid(True)
    # plt.show()
    return ar, sr, mdd

etfList = GetETF()
maxSR = 0
maxAR = 0
maxMDD = 0
maxSymbol = ""
resList = []
for symbol in etfList:
    try:
        ar, sr, mdd = Backtest(symbol)
        if ar > 0:
            maxSR = sr
            maxSymbol = symbol
            maxAR = ar
            maxMDD = mdd
            resList.append([maxSymbol, maxAR, maxSR, maxMDD])
    except: continue
    print(maxSymbol, maxAR, maxSR, maxMDD)
    df = pd.DataFrame(resList, columns=["symbol", "ar", "sr", "mdd"])
    df = df.sort_values(by='sr', ascending=False)
    df.to_csv("twAlphaETF.csv")
# Backtest("TQQQ")