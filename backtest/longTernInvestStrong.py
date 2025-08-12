import sys
sys.path.append('../')
from modules.aiztradingview import GetAll
import yfinance as yf
from datetime import datetime as dt, timedelta
from modules.shareholders import CheckIncomeIncrease
from modules.sharpe import GetMaxDD

symbolList = GetAll()

longTernDict = {'MRTN': 20.209999084472656, 'VIVO': 32.5099983215332, 'CMC': 35.7400016784668, 'GCBC': 49.709999084472656, 'ARTNA': 51.599998474121094, 'XEL': 68.86000061035156, 'PNW': 70.20999908447266, 'GIS': 74.37000274658203, 'WEC': 99.06999969482422, 'MGPI': 103.43000030517578, 'TRV': 158.35000610351562, 'ESLT': 232.32000732421875, 'ELV': 497.42999267578125, 'UNH': 533.4500122070312}

longTernDict = {'VIVO': 32.5099983215332, 'CMC': 35.7400016784668, 'GCBC': 49.709999084472656, 'ARTNA': 51.599998474121094, 'PNW': 70.20999908447266, 'WEC': 99.06999969482422, 'MGPI': 103.43000030517578, 'TRV': 158.35000610351562, 'ELV': 497.42999267578125, 'UNH': 533.4500122070312}

def GetDf(ticker):
    stockInfo = yf.Ticker(ticker)
    df = stockInfo.history(period="max")
    return df

def GetPerformance(ticker):
    try:
        df = GetDf(ticker)
        ipoPrice = df.iloc[0].Open
        if (df.iloc[0].Open == 0):
            for i in range(1, len(df)):
                if df.iloc[i].Open > 0:
                    ipoPrice = df.iloc[i].Open
                    break
        performance = df.iloc[-1].Close/ipoPrice
        return performance
    except: return 0

date = '2022-06-16'
timeD = dt.strptime(str(date), '%Y-%m-%d')
date = '2021-11-22'
timeD2 = dt.strptime(str(date), '%Y-%m-%d')

def GetRelativeStrengthPerformance(ticker):
    try:
        df = GetDf(ticker)
        mask = df.index <= str(timeD.date())
        df = df.loc[mask]
        mask = df.index >= str(timeD2.date())
        df = df.loc[mask]
        ipoPrice = df.iloc[0].Open
        if (df.iloc[0].Open == 0):
            for i in range(1, len(df)):
                if df.iloc[i].Open > 0:
                    ipoPrice = df.iloc[i].Open
                    break
        performance = df.iloc[-1].Close/ipoPrice
        return performance
    except: return 0

marketPerformance = GetPerformance('SPY')
print(marketPerformance)

relativeStrengthMarketPerformance = GetRelativeStrengthPerformance('SPY')
print(relativeStrengthMarketPerformance)

longTern = {}
for sym in symbolList:
    if CheckIncomeIncrease(sym):
        performance = GetPerformance(sym)
        if performance > marketPerformance:
            relativeStrengthPerformance = GetRelativeStrengthPerformance(sym)
            if relativeStrengthPerformance > 1:
                price = GetDf(sym).iloc[-1].Close
                print(sym,price)
                longTern[sym] = price

longTern = dict(sorted(longTern.items(), key=lambda item: item[1]))
print(longTern)