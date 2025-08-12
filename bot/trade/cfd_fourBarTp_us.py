import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail
from modules.trade.utils import GetVol
from ib_insync import *
from modules.strategy.fourBarTP import FourBarTP
from config import load_credentials
ACCOUNT = load_credentials('account')

ibc = ibc.Ib()
ib = ibc.GetIB(20)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)

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

def main():
    MIN_VOL = 1
    import pandas as pd
    df = pd.read_csv("cfd_fourBarTp_us.csv")
    symbolList = df["symbol"].values.tolist()
    symbolDict = {}
    for symbol in symbolList:
        symbolDict[symbol] = 1
    print(symbolDict)
    contractDict, cfdContractDict = GetContractDict(list(symbolDict.keys()))
    hourLimit = GetTradeTime()
    tf = '30 mins'
    lastOpMap = {}
    while(ib.sleep(60)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        minute = currentTime.minute
        t = hour * 60 + minute
        restrict = False
        if t < hourLimit * 60 + 30: 
            print(hour, minute)
            restrict = True
        elif t >= (hourLimit + 2) * 60:
        # elif t > (hourLimit + 7) * 60:
            print(hour, minute)
            restrict = True
        
        # RTH 22:30 - 06:00 JST
        # LOV VOL 03:50 - 06:00 JST
        if(
            t >= hourLimit * 60 + 30 and
            t < (hourLimit + 5) * 60 + 30
        ): 
            if t >= (hourLimit + 8) * 60:
                print("OUTSIDE RTH")
                print(f"START: {hourLimit}:30")
                print(f"END: {hourLimit + 8}:00")
            continue
        if hour == hourLimit + 7: continue
        tradeDict = {}
        for symbol, contract in contractDict.items():
            npArr = ibc.GetDataNpArr(contract, tf)
            if len(npArr) < 1: continue
            signal, op, sl, tp = FourBarTP(npArr, tf, tick_val=0.01)
            print(cfdContractDict[symbol].symbol)
            if signal == 0: continue
            bias = symbolDict[symbol]
            if bias != 0:
                if signal != bias: continue
            if op - sl < 0.3: continue
            tradeDict[symbol] = [signal, op, sl, tp]

        for symbol, res in tradeDict.items():
            signal, op, sl, tp = res
            closePos = False
            if signal != 0:
                msg = f'4btp {cfdContractDict[symbol].symbol} {tf} {signal} {op} {sl} {tp}'
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
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 1, 'USD')
                    print(symbol, vol)
                    if vol < MIN_VOL: continue
                    ExecTrail(ibc, signal, cfdContractDict[symbol], vol, op, sl, tp, closePos, False, ACCOUNT)
                    Alert(msg)
                    lastOpMap[symbol] = op
                else:
                    print(msg)
        
        print(cfdContractDict[symbol].symbol)

if __name__ == '__main__':
    main()