import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.fvg import Fvg
from modules.trade.futures import GetTradeTime, ExecTrailMOC
from modules.trade.utils import GetVol
from ib_insync import *

ibc = ibc.Ib()
ib = ibc.GetIB(18)

total_cash, exchangeRate = ibc.GetTotalCashExchangeRate()
print(total_cash)
total_cash /= exchangeRate

def GetContractDict(symbolList):
    contractDict = {}
    cfdContractDict = {}
    for symbol in symbolList:
        contract = Stock(symbol, 'TSEJ', 'JPY')
        ib.qualifyContracts(contract)
        contractDict[symbol] = contract
        contract = CFD(symbol, 'SMART', 'JPY')
        ib.qualifyContracts(contract)
        cfdContractDict[symbol] = contract
    return contractDict, cfdContractDict

def main():
    MIN_VOL = 100
    import pandas as pd
    df = pd.read_csv("cfd_fvg_2min_jp.csv")
    df = df[df['profitFactor'] > 4.38]
    symbolList = df["symbol"].values.tolist()
    symbolDict = {}
    for symbol in symbolList:
        symbolDict[symbol] = 1
    print(symbolDict)
    contractDict, cfdContractDict = GetContractDict(list(symbolDict.keys()))
    hourLimit = GetTradeTime()
    tf = '2 mins'
    lastOpMap = {}
    while(ib.sleep(15)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        minute = currentTime.minute
        if hour == 5 and minute == 55: 
            print("READEY TO CLOSE")
        if hour == 6: 
            print("CLOSE")
            continue
        if hour > 23: continue
        if hour <= 0 and minute <= 8: continue
        tradeDict = {}
        for symbol, contract in contractDict.items():
            npArr = ibc.GetDataNpArr(contract, tf)
            if len(npArr) < 1: continue
            signal, op, sl, tp = Fvg(npArr, tf, tick_val=1)
            print(cfdContractDict[symbol].symbol)
            if signal == 0: continue
            bias = symbolDict[symbol]
            if bias != 0:
                if signal != bias: continue
            tradeDict[symbol] = [signal, op, sl, tp]
        for symbol, res in tradeDict.items():
            signal, op, sl, tp = res
            closePos = False
            if signal != 0:
                msg = f'Fvg {cfdContractDict[symbol].symbol} {tf} {signal} {op} {sl} {tp}'
                trades = ibc.GetOpenTrades()
                for trade in trades:
                    if trade.contract == cfdContractDict[symbol]:
                        if trade.order.action == 'BUY':
                            if signal > 0:
                                print(f'Pending BUY Order {trade.contract.symbol}')
                                continue
                            elif signal < 0:
                                closePos = True
                        elif trade.order.action == 'SELL':
                            if signal < 0:
                                print(f'Pending SELL Order {trade.contract.symbol}')
                                continue
                            elif signal > 0:
                                closePos = True
                if symbol not in lastOpMap or op != lastOpMap[symbol]:
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 1, 'JPY')
                    print(symbol, vol)
                    if vol < MIN_VOL: continue
                    ExecTrailMOC(ibc, signal, cfdContractDict[symbol], vol, op, sl, tp, closePos, False)
                    Alert(msg)
                    lastOpMap[symbol] = op
                else:
                    print(msg)
            print(cfdContractDict[symbol].symbol)

if __name__ == '__main__':
    main()