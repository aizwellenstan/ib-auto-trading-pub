from __future__ import (absolute_import, division, print_function, unicode_literals)
from Copula_Pair_Trading_backtrader_Strategy_class import *
from PerformanceTracker import *
import glob
import pandas as pd
import datetime
import backtrader as bt

import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import pandas_ta as ta
from backtesting import Backtest, Strategy
import modules.ib as ibc
from modules.strategy.copula import Copula
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade
from modules.aiztradingview import GetIndexHoldingsJP, GetLiquidETF
from ib_insync import *

ibc = ibc.Ib()
ib = ibc.GetIB(29)

contractES, contractNQ, contractMNQ, contractMES, contractTOPX, contractMNTPX, contractMCL, contractN225, contractN225M, contractN225MC, contractMHI, contractDJIA, contractMGC,  contractJPY, contractNKD = GetFuturesContracts(ib)


class CommInfoFractional(bt.CommissionInfo):

    def getsize(self, price, cash):

        return self.p.leverage * (cash / price)

class TestStrat(bt.Strategy):

    def __init__(self):
        self.price = self.datas[0].close
        self.flag = True
        self.index = 0

    def next(self):

        self.index = self.index + 1

        if self.index == 2:
            print(self.position)
            print(not self.position)

if __name__ == '__main__':

    # Flag to indicating whether it is optimization process

    optimize = False

    print_log = True

    # if optimize :

    #     params_set = [30 * 24 , 60 * 24 , 90 * 24 , 120 * 24 , 150 * 24 , 180 * 24 , 210 * 24, 240 * 24, 270 * 24, 300 * 24, 330 * 24, 360 * 24]

    # else :

    #     params_set = [360*24]

    # for window in params_set:

    cerebro = bt.Cerebro()

    cerebro.addstrategy(CopulaStrat, copula_threshold = 0.01, printlog = print_log)

    cerebro.broker.setcash(6000.0)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.broker.set_slippage_perc(0.001)
    cerebro.broker.addcommissioninfo(CommInfoFractional())

    # path = '/Users/ccm/Desktop/Trading/Algo/Data/Crypto/CCXT Data/Hourly/*'
    
    tf = '5 mins'
    contractYM = Future(conId=672387412, symbol='YM', lastTradeDateOrContractMonth='20241220', multiplier='5', currency='USD', localSymbol='YMZ4', tradingClass='YM')
    ib.qualifyContracts(contractYM)
    dfNQ = ibc.GetDataDf(contractNQ, tf)
    dfNQ.set_index('date', inplace=True)
    dfES = ibc.GetDataDf(contractES, tf)
    dfES.set_index('date', inplace=True)
    dfYM = ibc.GetDataDf(contractYM, tf)
    dfYM.set_index('date', inplace=True)
    contractAAPL = Stock("KO", 'SMART', 'USD')
    ib.qualifyContracts(contractAAPL)
    dfAAPL = ibc.GetDataDf(contractAAPL, tf)
    dfAAPL.set_index('date', inplace=True)
    contractMSFT = Stock("PEP", 'SMART', 'USD')
    ib.qualifyContracts(contractMSFT)
    dfMSFT = ibc.GetDataDf(contractMSFT, tf)
    dfMSFT.set_index('date', inplace=True)


    data = bt.feeds.PandasData(
        dataname=dfAAPL,
        timeframe=bt.TimeFrame.Minutes,
        compression=5,
        fromdate=datetime.datetime(2024, 9, 7),
        todate=datetime.datetime(2024, 10, 7)
    )

    name = 'AAPL'

    cerebro.adddata(data, name=name)

    data = bt.feeds.PandasData(
        dataname=dfMSFT,
        timeframe=bt.TimeFrame.Minutes,
        compression=5,
        fromdate=datetime.datetime(2024, 9, 7),
        todate=datetime.datetime(2024, 10, 7)
    )

    name = 'MSFT'

    cerebro.adddata(data, name=name)

    for data in cerebro.datas:
        data.plotinfo.plot = False

    cerebro.addanalyzer(PortfolioPerformance, _name='portfolioperformance', annualizedperiod=365*24)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    strat = cerebro.run(maxcpus=1)

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    if optimize:
        print('sample_window : %2f' % window)

    print('*******Strategy Performance**********')

    performance = strat[0].analyzers.portfolioperformance.get_analysis()

    print('Total Period (Log) Return : %f' % performance['periodreturn'])

    print('Annualized (Log) Return : %f' % performance['annualizedreturn'])

    print('Sharpe Ratio: %f' % performance['sharperatio'])

    print('MDD: %f' % performance['MDD'])

    print('Calmar Ratio : %f' % (performance['annualizedreturn'] / performance['MDD']))

    tradeanalysis = strat[0].analyzers.tradeanalyzer.get_analysis()

    print('Total Trade : %f' % tradeanalysis.total.total)
    # print('Total PnL : %f' % tradeanalysis.pnl.net.total)
    # print('Win Rate : %f' % (int(tradeanalysis.won.total) / int(tradeanalysis.total.total)))
    # print('Average Win Trade Profit : %f' % tradeanalysis.won.pnl.average)
    # print('Average Loss Trade Profit : %f' % tradeanalysis.lost.pnl.average)
    # print('Average Trading Period : %f' % tradeanalysis.len.average)

    print('********End**********')

    if not optimize:
        cerebro.plot()