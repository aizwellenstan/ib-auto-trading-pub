import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import pandas_ta as ta
from backtesting import Backtest, Strategy
import modules.ib as ibc
from modules.strategy.fvg import Fvg
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade
from modules.aiztradingview import GetIndexHoldingsJP, GetLiquidETF
from ib_insync import *

def time_to_minutes(time_str):
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

JP_START = time_to_minutes("09:00")
JP_END = time_to_minutes("15:00")
NY_START = time_to_minutes("22:30")
NY_END = time_to_minutes("23:00")
NY2_START = time_to_minutes("00:00")
NY2_END = time_to_minutes("01:00")
# NY_END = time_to_minutes("23:10") #10 mins
def is_ny_op(time_str):
    time_in_minutes = time_to_minutes(time_str)
    # return time_in_minutes >= NY_START and time_in_minutes < NY_END 
    # return time_in_minutes >= JP_START and time_in_minutes < JP_END
    return (
        (time_in_minutes >= NY_START and time_in_minutes <= NY_END) 
        # or
        # (time_in_minutes >= NY2_START and time_in_minutes <= NY2_END) 
    )
ibc = ibc.Ib()
ib = ibc.GetIB(25)

# indexHoldings = GetIndexHoldingsJP()
liquidEtfs = GetLiquidETF()
# print(indexHoldings)
df = pd.read_csv(f"{rootPath}/data/ib_cfd_us.csv")
cfd = df['Symbol'].values.tolist()

symbolList = [s for s in liquidEtfs if s in cfd]
# for s in liquidEtfs:
#     if s in cfd:
#         symbolList.append(s)
print(symbolList)

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

# contractN225 = Future(conId=618689007, symbol='N225', lastTradeDateOrContractMonth='20240912', multiplier='1000', currency='JPY', localSymbol='169090018', tradingClass='N225')
# ib.qualifyContracts(contractN225)
# contractMNTPX = Future(conId=670498961, symbol='MNTPX', lastTradeDateOrContractMonth='20240912', multiplier='1000', currency='JPY', localSymbol='169090006', tradingClass='TPXM')
# ib.qualifyContracts(contractMNTPX)
# contractNKD = Future(conId=513398738, symbol='NKD', lastTradeDateOrContractMonth='20240912', multiplier='5', currency='USD', localSymbol='NKDU4', tradingClass='NKD')
# ib.qualifyContracts(contractNKD)
# contractES = Future(conId=568550526, symbol='ES', lastTradeDateOrContractMonth='20240920', multiplier='50', currency='USD', localSymbol='ESU4', tradingClass='ES')
# ib.qualifyContracts(contractES)
# contractGC = Future(conId=347896248, symbol='GC', lastTradeDateOrContractMonth='20241227', multiplier='100', currency='USD', localSymbol='GCZ4', tradingClass='GC')
# ib.qualifyContracts(contractGC)
# symbolList = ["EWJ", "AAPL"]
# contractDict, cfdContractDict = GetContractDict(symbolList)
# contract = contractDict["EWJ"]
contractES, contractNQ, contractMNQ, contractMES, contractTOPX, contractMNTPX, contractMCL, contractN225, contractN225M, contractN225MC, contractMHI, contractDJIA, contractMGC,  contractJPY, contractNKD = GetFuturesContracts(ib)
# contract = Stock('6016', 'TSEJ', 'JPY')

"""timeframes
1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins,
10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 
8 hours, 1 day, 1W, 1M
"""
tf = '5 mins'
tradable = []
allSymbol = []
# df = pd.read_csv("cfd_fvg_jp.csv")
# df.columns = ["i","symbol"]
# symbolList = df["symbol"].values.tolist()
res = []
symbolList = ["QQQ"]
for symbol in symbolList:
    try:
        # contract = Stock(symbol, 'TSEJ', 'JPY')
        contract = Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        df = ibc.GetDataDf(contractMNQ, tf)
        df2 = ibc.GetDataDf(contract, tf)
        # df['date'] = pd.to_datetime(df1['date'])
        # df2['date'] = pd.to_datetime(df2['date'])

        # Drop rows in df1 where 'Date' is not in df2
        df = df[df['date'].isin(df2['date'])]
        dfOri = df
        df2 = df2[df2['date'].isin(df['date'])]
        print(len(df), len(df2))

        df1 = df.join(df2, lsuffix='', rsuffix='_df2')
        # Overwrite columns
        df1[['open', 'high', 'low', 'close']] = df1[['open_df2', 'high_df2', 'low_df2', 'close_df2']]
        df1 = df1.drop(columns=['open_df2', 'high_df2', 'low_df2', 'close_df2'])
        df = df1
        print("--------")
        print(df1)
        print(df2)
    except Exception as e: 
        print(e)
        continue
    
    df['Open'] = df['open']
    df['High'] = df['high']
    df['Low'] = df['low']
    df['Close'] = df['close']
    df['Volume'] = df['volume']
    dfOri['Open'] = dfOri['open']
    dfOri['High'] = dfOri['high']
    dfOri['Low'] = dfOri['low']
    dfOri['Close'] = dfOri['close']
    dfOri['Volume'] = dfOri['volume']
    print(df)

    oriNpArr = df[['Open', 'High', 'Low', 'Close']].to_numpy()
    oriNpArr2 = dfOri[['Open', 'High', 'Low', 'Close']].to_numpy()
    print(oriNpArr)
    from modules.trade.utils import floor_round, ceil_round
    def GetOPSLTP(npArr, signal, tf, tick_val):
        TP_VAL = 2.489
        if tf in ['20 mins']: TP_VAL = 4
        elif tf in ['30 mins']: TP_VAL = 2
        elif tf in ['10 mins']: TP_VAL = 5
        if signal > 0:
            op = npArr[-1][0]
            sl = np.min(npArr[-3:][:,2])
            tp = op + (op-sl) * TP_VAL
            tp = floor_round(tp, tick_val)
        else:
            op = npArr[-1][0]
            sl = np.max(npArr[-3:][:,1])
            tp = op - (sl-op) * TP_VAL
            tp = ceil_round(tp, tick_val)
        return op, sl, tp
    
    TotalSignal = []
    SlSignal = []
    TpSignal = []
    trades = []
    for i in range(0, len(oriNpArr)):
        npArr = oriNpArr[:i+2]
        signal, op, sl, tp = Fvg(npArr, tf)
        npArr = oriNpArr2[:i+2]
        op, sl, tp = GetOPSLTP(npArr, signal, tf, 1)
        TotalSignal.append(signal)
        SlSignal.append(sl)
        TpSignal.append(tp)
        if signal != 0:
            trades.append([op, sl, tp])
    print(TotalSignal)
    print(len(TotalSignal), len(dfOri))
    # sys.exit()
    dfOri['TotalSignal'] = TotalSignal
    dfOri['SlSignal'] = SlSignal
    dfOri['TpSignal'] = TpSignal

    print(dfOri['TotalSignal'])
    # Define SIGNAL function for backtesting
    def SIGNAL():
        return dfOri.TotalSignal

    # Define strategy class for backtesting
    compare = []

    class MyStrat(Strategy):
        initsize = 0.99
        mysize = initsize

        def init(self):
            super().init()
            self.signal1 = self.I(SIGNAL)
            print(self.signal1)

        def next(self):
            super().next()

            # if len(self.trades) > 0:
            #     dt = self.data.date[-1]
            #     time_str = str(dt)[11:16]
            #     if self.trades[-1].is_long and not is_ny_op(time_str):
            #         self.trades[-1].close()
            #     if self.trades[-1].is_short and not is_ny_op(time_str):
            #         self.trades[-1].close()

            if self.signal1 == 1 and len(self.trades) == 0:
                sl1 = self.data.SlSignal[-1]
                tp1 = self.data.TpSignal[-1]
                dt = self.data.date[-1]
                time_str = str(dt)[11:16]
                # Extract the time component from numpy.datetime64 and compare
                if is_ny_op(time_str):
                    print(self.data)
                    compare.append([self.data.Open[-1], sl1, tp1])
                    try:
                        self.buy(sl=sl1, tp=tp1, size=self.mysize)
                    except:
                        print(symbol, sl, tp)
                        print(self.data)

            # elif self.signal1 == -1 and len(self.trades) == 0:
            #     sl1 = self.data.SlSignal[-1]
            #     tp1 = self.data.TpSignal[-1]
            #     dt = self.data.date[-1]
            #     time_str = str(dt)[11:16]
            #     # Extract the time component from numpy.datetime64 and compare
            #     if is_ny_op(time_str):
            #         compare.append([self.data.Open[-1], sl1, tp1])
            #         try:
            #             self.sell(sl=sl1, tp=tp1, size=self.mysize)
            #         except:
            #             print(symbol, sl, tp)
            #             print(self.data)

    # Perform backtest
    bt = Backtest(dfOri, MyStrat, cash=100000, margin=1/10, commission=0.00)
    stat = bt.run()
    print(trades)
    print("COMPARE",compare)
    print("----------")
    # Print backtest statistics
    print(stat)
    # returns = stat['Return [%]']
    # sharpe = stat['Sharpe Ratio']
    # sortino = stat['Sortino Ratio']
    # calmar = stat['Calmar Ratio']
    # returns_ann = stat['Return (Ann.) [%]']
    # profitFactor = stat['Profit Factor']
    # if (
    #     sharpe > 0.0004 and profitFactor > 2 and
    #     sortino > 122 and returns_ann > 30
    # ):
    #     tradable.append([symbol, returns, sharpe, sortino, calmar, returns_ann, profitFactor])
    #     df = pd.DataFrame(tradable)
    #     df.columns = ["symbol", "returns", "sharpe", "sortino", "calmar", "returns_ann", "profitFactor"]
    #     df.to_csv('mnq_etf_fvg_signal.csv')

    # allSymbol.append([symbol, returns, sharpe, sortino, calmar, returns_ann, profitFactor])
    # df = pd.DataFrame(allSymbol)
    # df.columns = ["symbol", "returns", "sharpe", "sortino", "calmar", "returns_ann", "profitFactor"]
    # df.to_csv('mnq_etf_fvg_signal_all.csv')