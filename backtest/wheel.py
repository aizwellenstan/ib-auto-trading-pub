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
from modules.strategy.ma import SmaSR, SimpleMaCrossOver, SimpleMaCross, OriSimpleMaCross, MaCrossHTF
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade
from modules.aiztradingview import GetClose, GetIndexHoldingsJP, GetLiquidETF
from ib_insync import *

ibc = ibc.Ib()
ib = ibc.GetIB(26)

closeDict = GetClose()

closeDict = dict(sorted(closeDict.items(), key=lambda item: item[1]))

for symbol in closeDict:
    if closeDict[symbol] < 5: continue
    contract = Stock(symbol, 'SMART', 'USD')
    ib.qualifyContracts(contract)
    chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)
    if len(chains) < 1: continue
    print(symbol)
    break