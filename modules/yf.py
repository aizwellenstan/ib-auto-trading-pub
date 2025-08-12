import yfinance as yf
from datetime import datetime
# import pandas as pd
def GetData(symbol):
    stockInfo = yf.Ticker(symbol)
    df = stockInfo.history(period="60d", interval = "30m")
    df = df.assign(date=df.index.tz_convert('Asia/Tokyo').tz_localize(None))
    df = df.assign(open=df.Open)
    df = df.assign(high=df.High)
    df = df.assign(low=df.Low)
    df = df.assign(close=df.Close)
    df = df.assign(volume=df.Volume)
    df = df[['date','open','high','low','close','volume']]

    return df

# df = GetData('QQQ')
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(df)

# import numpy as np
# import yfinance as yf
# import pandas as pd

# # function getting data for the last x years with x weeks space 
# # from checking data and specific observation.
# def stock_data(ticker, period, interval, observation):
#     ticker = yf.Ticker(ticker)
#     ticker_history = ticker.history(period, interval)
#     print((ticker_history[observation])) 

#     sf = ticker_history[observation]
#     df = pd.DataFrame({'Date':sf.index, 'Values':sf.values})

#     print(df)
# if __name__ == '__main__':
#     stock_data('GOOGL', '7d', '1m', 'Open')

# data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     # print(data['Volume']['AAPL'].head())
#     print(hist['Volume'].tail())
# hist.drop(hist[hist.index > '2021-09-01'].index, inplace=True)
# print(hist)
# preAvgVol = hist['Volume'].iloc[1:4:1].mean()
# todayVol = hist['Volume'][-1]

# print(preAvgVol,todayVol)
# symbolNames = ""
# for trade in trades:
#     symbol = str(trade['symbol'])
#     symbolNames += symbol
#     symbolNames += " "
# yfData = yf.download(symbolNames, start="2021-03-01", end="2021-10-28")
# print(yfData)
# stockInfo = yf.Ticker(symbol)
# hist = stockInfo.history(period="365d")
# print(hist)
# hist.drop(hist[hist['Date'] > backtestDate].index, inplace=True)
# print(hist)
# preAvgVol = hist['Volume'].iloc[1:4:1].mean()
# todayVol = hist['Volume'][-1]

# print(preAvgVol,todayVol)

# try:
#     hist = yfData.drop(yfData[yfData.index >= backtestDate].index, inplace=True)
#     print
#     preAvgVol = hist['Volume'][symbol].iloc[1:4:1].mean()
#     todayVol = hist['Volume'][symbol][-1]
    
#     print(todayVol,preAvgVol)
# except:
#     pass