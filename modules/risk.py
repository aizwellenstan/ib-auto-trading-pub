import pandas as pd
import numpy as np
import sys
mainFolder = '../'
sys.path.append(mainFolder)
from modules.riskOfRuin import calcRisk

def GetMaxDD(df):
    column = df.columns[0]
    pctChange = df[column].pct_change().dropna()
    wealthIdx = 1*(1+pctChange).cumprod()
    previousPeaks = wealthIdx.cummax()
    dd = (wealthIdx-previousPeaks)/previousPeaks
    maxDD = min(dd)
    
    return maxDD

def GetDDDuration(df):
    column = df.columns[0]
    pctChange = df[column].pct_change().dropna()
    wealthIdx = 1*(1+pctChange).cumprod()
    previousPeaks = wealthIdx.cummax()
    dd = (wealthIdx-previousPeaks)/previousPeaks
    maxDD = min(dd)
    ddArr = dd.values.tolist()
    ddIdx = 0
    recoverDD = maxDD
    recoverDDIdx = 0
    maxDDApper = False
    for idx, val in enumerate(ddArr):
        if val <= maxDD:
            ddIdx = idx
            maxDDApper = True
        if maxDDApper:
            if val > recoverDD:
                recoverDD = val
                recoverDDIdx = idx
    recoverDuration = recoverDDIdx - ddIdx
    if recoverDuration < 1: recoverDuration = 1

    return recoverDuration


def GetWinRate(df,column='Close'):
    gapUp = (
        df.Open > df.Close.shift(1)
    )
    up = df.Close>df.Open
    down = df.Close<df.Open
    # up = up.replace({True: 1, False: 0})
    # down = down.replace({True: 1, False: 0})
    up=up.astype(int)
    down=down.astype(int)
    df = df.assign(up=up)
    df = df.assign(down=down)
    up = df.loc[gapUp, 'up']
    down = df.loc[gapUp, 'down']
    wr = up.sum()/(up.sum()+down.sum())
    
    return wr

def GetR(df):
    bullCandle = (
        df.Close > df.Open
    )
    gapUp = (
        df.Open > df.Close.shift(1)
    )
    df = df.dropna()
    df = df.assign(
        r=(df.Close-df.Open)/(df.Open-df.Close.shift(1))
    )
    r = df.loc[bullCandle & gapUp, 'r'].mean()

    return r

def GetRiskOfRuin(df):
    wr = GetWinRate(df)
    r = GetR(df)
    riskOfRuin = calcRisk(r,wr,100)

    return riskOfRuin

# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="365d")

# # wr = GetWinRate(df)
# # print(wr)
# df = df[['Close']]
# maxDDDur = GetDDDuration(df)
# print(maxDDDur)