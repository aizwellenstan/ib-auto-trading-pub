import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import pandas_ta as ta
from backtesting import Backtest, Strategy
from modules.strategy.emaCross import EmaCrossStrategy

import modules.ib as ibc
from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade


# # ticker = "NKD=F"
# # ticker = "ES=F"
# ticker = "GC=F"

# # # Define the start and end dates for the data
# # start_date = datetime.datetime.now() - datetime.timedelta(days=60)  # 30 days ago
# # end_date = datetime.datetime.now()

# # # Fetch the data from Yahoo Finance
# # df = yf.download(ticker, start=start_date, end=end_date, interval="5m")

# # Fetch the data from Yahoo Finance
# fPath = f"{ticker}.parquet"
# # df.to_parquet(fPath)
# df = pd.read_parquet(fPath)
def GetContractDict(symbolList):
    contractDict = {}
    cfdContractDict = {}
    for symbol in symbolList:
        contract = Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        contractDict[symbol] = contract
        contract = CFD(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        cfdContractDict[symbol] = contract
    return contractDict, cfdContractDict

ibc = ibc.Ib()
ib = ibc.GetIB(16)
from ib_insync import *
# contractN225 = Future(conId=618689007, symbol='N225', lastTradeDateOrContractMonth='20240912', multiplier='1000', currency='JPY', localSymbol='169090018', tradingClass='N225')
# ib.qualifyContracts(contractN225)
# contractMNTPX = Future(conId=670498961, symbol='MNTPX', lastTradeDateOrContractMonth='20240912', multiplier='1000', currency='JPY', localSymbol='169090006', tradingClass='TPXM')
# ib.qualifyContracts(contractMNTPX)
# contractNKD = Future(conId=513398738, symbol='NKD', lastTradeDateOrContractMonth='20240912', multiplier='5', currency='USD', localSymbol='NKDU4', tradingClass='NKD')
# ib.qualifyContracts(contractNKD)
contractES = Future(conId=568550526, symbol='ES', lastTradeDateOrContractMonth='20240920', multiplier='50', currency='USD', localSymbol='ESU4', tradingClass='ES')
ib.qualifyContracts(contractES)
# contractGC = Future(conId=347896248, symbol='GC', lastTradeDateOrContractMonth='20241227', multiplier='100', currency='USD', localSymbol='GCZ4', tradingClass='GC')
# ib.qualifyContracts(contractGC)
# symbolList = ["EWJ", "AAPL"]
# contractDict, cfdContractDict = GetContractDict(symbolList)
# contract = contractDict["EWJ"]

# contract = Stock('6315', 'TSEJ', 'JPY')
# ib.qualifyContracts(contract)

"""
symbol | sr   | sortino
N225   | 0.72 | 1.43
"""

contractES, contractNQ, contractMNQ, contractMES, contractN225, contractN225M, contractN225MC, contractMNTPX, contractDJIA, contractMGC, contractQQQ = GetFuturesContracts(ib)
df = ibc.GetDataDf(contractMNQ, '1 min')
df['Open'] = df['open']
df['High'] = df['high']
df['Low'] = df['low']
df['Close'] = df['close']
df['Volume'] = df['volume']
print(df)

df = EmaCrossStrategy(df)
# Apply ATR calculation using pandas_ta
dfpl = df[:75000].copy()
dfpl['ATR'] = ta.atr(dfpl.High, dfpl.Low, dfpl.Close, length=7)

# Define SIGNAL function for backtesting
def SIGNAL():
    return dfpl.TotalSignal

# Define strategy class for backtesting
class MyStrat(Strategy):
    initsize = 0.99
    mysize = initsize

    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)

    def next(self):
        super().next()
        slatr = 1.2 * self.data.ATR[-1]
        TPSLRatio = 1.6

        # if len(self.trades) > 0:
        #     if self.trades[-1].is_long and self.data.Close[-1] < self.data.EMA_Fast[-1]:
        #         self.trades[-1].close()
        #     elif self.trades[-1].is_short and self.data.Close[-1] > self.data.EMA_Fast[-1]:
        #         self.trades[-1].close()

        if self.signal1 == 2 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] - slatr
            tp1 = self.data.Close[-1] + slatr * TPSLRatio
            self.buy(sl=sl1, tp=tp1, size=self.mysize)

        elif self.signal1 == 1 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] + slatr
            tp1 = self.data.Close[-1] - slatr * TPSLRatio
            self.sell(sl=sl1, tp=tp1, size=self.mysize)

# Perform backtest
bt = Backtest(dfpl, MyStrat, cash=100000, margin=1/10, commission=0.00)
stat = bt.run()

# Print backtest statistics
print(stat)
