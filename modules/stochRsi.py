import pandas as pd
import sys
mainFolder = '../'
sys.path.append(mainFolder)
from modules.vwap import Vwma
from modules.movingAverage import Ema

def GetStochRsi(df, column='Close'):
    delta = df[column].diff(1)
    delta = delta.dropna()
    up = delta.copy()
    down = delta.copy()
    up[up<0] = 0
    down[down>0] = 0
    df = df.assign(up=up)
    df = df.assign(down=down)
    v = df.Volume.values
    upArr = df.up.values
    downArr = df.down.values
    avgGain = Ema(upArr,20)
    avgLoss = abs(Ema(downArr,20))
    rs = avgGain / avgLoss
    rsi = 100.0 - (100.0 / (1.0 + rs))[-1]

    return rsi

def EMA(df, period=20, column='Close'):
    return df[column].ewm(span=period, adjust=False).mean()

def GetRsi2(df, column='Close'):
    delta = df[column].diff(1)
    delta = delta.dropna()
    up = delta.copy()
    down = delta.copy()
    up[up<0] = 0
    down[down>0] = 0
    df = df.assign(up=up)
    df = df.assign(down=down)
    # v = df.Volume.values
    # upArr = df.up.values
    # downArr = df.down.values
    avgGain = EMA(df, column='up')
    avgLoss = abs(EMA(df, column='down'))
    rs = avgGain / avgLoss
    rsi = 100.0 - (100.0 / (1.0 + rs))[-1]

    return rsi

def GetStochRsi2(df, period=20,column='Close'):
    delta = df[column].diff(1)
    delta = delta.dropna()
    up = delta.copy()
    down = delta.copy()
    up[up<0] = 0
    down[down>0] = 0
    df = df.assign(up=up)
    df = df.assign(down=down)
    # v = df.Volume.values
    # upArr = df.up.values
    # downArr = df.down.values
    avgGain = EMA(df, column='up')
    avgLoss = abs(EMA(df, column='down'))
    rs = avgGain / avgLoss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    stochRsi = (
        (rsi - rsi.rolling(period).min()) /
        (rsi.rolling(period).max()-rsi.rolling(period).min())
    )[-1]

    return stochRsi

# import yfinance as yf
# stockInfo = yf.Ticker("SPY")
# df = stockInfo.history(period="365d")
# stochRsi = GetStochRsi2(df)
# print(stochRsi)
