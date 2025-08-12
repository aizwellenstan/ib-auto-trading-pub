import sys
sys.path.append('../')
from modules.aiztradingview import GetAll
import yfinance as yf
from datetime import datetime as dt, timedelta
from modules.shareholders import CheckIncomeIncrease
from modules.sharpe import GetMaxDD

symbolList = GetAll()

longTernDict = {'MRTN': 20.209999084472656, 'SHEN': 21.280000686645508, 'PHI':
29.15999984741211, 'VIVO': 32.5099983215332, 'AROW': 32.58000183105469, 'GABC': 34.790000915527344, 'CMC': 35.7400016784668, 'UBSI': 36.439998626708984, 'YORW': 41.65999984741211, 'NRIM': 41.720001220703125, 'WTRG': 47.43000030517578, 'FAST': 48.5, 'WASH': 49.650001525878906, 'GCBC': 49.709999084472656, 'ARTNA': 51.599998474121094, 'LKQ': 52.7599983215332, 'PLUS': 52.849998474121094, 'WABC': 56.099998474121094, 'LNT': 57.16999816894531, 'SEE':
57.75, 'TD': 63.68000030517578,
'OTTR': 67.12000274658203, 'XEL': 68.86000061035156, 'PNW': 70.20999908447266, 'CP': 73.94999694824219, 'GIS': 74.37000274658203, 'ENSG': 76.0199966430664, 'MGEE': 76.69999694824219, 'CLFD': 78.37999725341797, 'PLXS': 81.30999755859375, 'CHD': 94.08999633789062, 'WEC': 99.06999969482422, 'CRMT': 99.12000274658203, 'MGPI': 103.43000030517578, 'USLM':
105.22000122070312, 'IDA': 105.94000244140625, 'UHS': 107.72000122070312, 'ABT': 109.93000030517578, 'NVO': 115.81999969482422,
'CPK': 128.05999755859375, 'DGX': 136.66000366210938, 'TRV': 158.35000610351562, 'MED': 173.74000549316406, 'GPI': 177.6999969482422, 'CASY': 198.91000366210938, 'TSCO': 205.6300048828125, 'ADP': 218.9499969482422, 'APD': 230.0, 'ESLT': 232.32000732421875, 'LAD': 295.55999755859375, 'SNPS': 323.510009765625, 'ELV': 497.42999267578125, 'COST': 520.22998046875, 'UNH': 533.4500122070312, 'TMO': 536.8699951171875, 'ORLY': 689.3200073242188}

longTernDict = {'SHEN': 21.280000686645508, 'PHI': 29.15999984741211, 'VIVO': 32.5099983215332, 'AROW': 32.58000183105469, 'GABC': 34.790000915527344, 'CMC': 35.7400016784668, 'UBSI': 36.439998626708984, 'YORW': 41.65999984741211, 'WTRG':
47.43000030517578, 'FAST': 48.5, 'WASH': 49.650001525878906, 'GCBC': 49.709999084472656, 'ARTNA': 51.599998474121094, 'WABC': 56.099998474121094, 'LNT': 57.16999816894531, 'SEE': 57.75, 'OTTR': 67.12000274658203, 'XEL': 68.86000061035156, 'PNW': 70.20999908447266, 'CP': 73.94999694824219, 'MGEE': 76.69999694824219, 'PLXS': 81.30999755859375, 'CHD': 94.08999633789062, 'WEC': 99.06999969482422, 'CRMT': 99.12000274658203, 'MGPI': 103.43000030517578, 'USLM': 105.22000122070312, 'IDA': 105.94000244140625, 'UHS': 107.72000122070312, 'ABT': 109.93000030517578, 'CPK': 128.05999755859375, 'DGX': 136.66000366210938, 'TRV': 158.35000610351562, 'TSCO': 205.6300048828125, 'ADP': 218.9499969482422, 'APD': 230.0, 'LAD': 295.55999755859375, 'ELV': 497.42999267578125, 'COST': 520.22998046875, 'UNH': 533.4500122070312, 'TMO': 536.8699951171875, 'ORLY': 689.3200073242188}

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
            if relativeStrengthPerformance > relativeStrengthMarketPerformance:
                price = GetDf(sym).iloc[-1].Close
                print(sym,price)
                longTern[sym] = price

longTern = dict(sorted(longTern.items(), key=lambda item: item[1]))
print(longTern)