import sys
sys.path.append('../')
from modules.aiztradingview import GetLongTern
import yfinance as yf
from datetime import datetime as dt, timedelta

longTern = GetLongTern()

date = '2022-06-16'
timeD = dt.strptime(str(date), '%Y-%m-%d')
date = '2021-11-22'
timeD2 = dt.strptime(str(date), '%Y-%m-%d')
date = '2022-03-29'
timeD3 = dt.strptime(str(date), '%Y-%m-%d')

stockInfo = yf.Ticker('SPY')
df = stockInfo.history(period="max")
marketPerformance = df.iloc[-1].Close/df.iloc[0].Open
print(marketPerformance)

# ['MRK', 'IBM', 'BMY', 'VIVO', 'PLAB', 'FCUV', 'AZPN', 'UTHR',
# 'PRPH']
# longTern = ['IBM', 'VIVO', 'FCUV', 'PRPH']
# ['SIGA', 'VERU', 'IBM', 'BLTE', 'VIVO', 'TPTX', 'PRPH', 'MXC', 'FCUV', 'NVCT']

def CheckPerformance(sym):
    global marketPerformance
    try:
        stockInfo = yf.Ticker(sym)
        df = stockInfo.history(period="max")
        if df.iloc[-1].Close/df.iloc[0].Open < marketPerformance:
            return False
        if df.iloc[-1].Close/df.iloc[0].Open < 1:
            return False
        mask = df.index <= str(timeD.date())
        df1 = df.loc[mask]
        mask = df1.index >= str(timeD2.date())
        df1 = df1.loc[mask]
        performance = df1.iloc[-1].Close/df1.iloc[0].Open
        mask = df1.index >= str(timeD3.date())
        df1 = df1.loc[mask]
        performance2 = df1.iloc[-1].Close/df1.iloc[0].Open

        # mask = df.index <= str(timeD3.date())
        # df2 = df.loc[mask]
        # mask = df2.index >= str(timeD4.date())
        # df2 = df2.loc[mask]
        # performance2 = df2.iloc[-1].Close/df2.iloc[0].Open
        print(sym,performance,performance2)
        if performance > 1 and performance2 > 1:
            return True
        return False
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return False

investList = []
for sym in longTern:
    if CheckPerformance(sym):
        investList.append(sym)
print(investList)
    