import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.ma import SimpleMaCrossOver
from modules.strategy.manipulationBlock import Mb
from modules.strategy.vTurn import VTurn
from modules.strategy.ob import ObFiveMin
from modules.strategy.emaV2 import EmaCross
from modules.strategy.fourBarTP import FourBarTP
from modules.strategy.vsa import NoSupplyBar
from modules.strategy.donchainChannel import DcBreakOut
from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
from modules.strategy.fvg import HpFvg, Fvg
from modules.strategy.combine import Combine
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail, ExecTrailMOC, cancelUntriggeredAll
from modules.trade.utils import GetVol
from ib_insync import Stock, CFD
import pandas as pd
from modules.strategy.threeBarPlay import ThreeBarPlay
from modules.strategy.irb import HpIrb
from config import load_credentials
ACCOUNT = load_credentials('stockAccount')
STOCKACCOUNT = load_credentials('stockAccount')

ibc = ibc.Ib()
ib = ibc.GetIB(8)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
# total_cash *= 4 # margin
total_cash /= 2
print(total_cash)

stock_total_cash, stock_avalible_cash = ibc.GetTotalCash(STOCKACCOUNT)
# print(stock_total_cash)
stock_total_cash /= 3

contractES, contractNQ, contractMNQ, contractMES, contractTOPX, contractMNTPX, contractMCL, contractN225, contractN225M, contractN225MC, contractMHI, contractDJIA, contractMGC,  contractJPY, contractNKD = GetFuturesContracts(ib)
contractQQQ = Stock("QQQ", 'SMART', 'USD')
contractIVV = Stock('IVV', 'SMART', 'USD')
ib.qualifyContracts(contractIVV)

tradeDict = {}

def CheckSimpleMaCrossOver(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2200-2300
    strategy: mes 5 mins 10 25 simple ma cross
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = SimpleMaCrossOver(npArr, tf, tick_val=0.25)
    if signal == 0: return 0
    sType = "10 25 SIMPLE MA CROSS"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckHpFvg(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2200-2300
    strategy: mes 5 mins fvg
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = HpFvg(npArr, tf, tick_val=1)
    if signal == 0: return 0
    sType = "FVG"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckHpIrb(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-2330
    strategy: mes 5 mins hpirb
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = HpIrb(npArr, tf, tick_val=1)
    if signal == 0: return 0
    sType = "HPIRB"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckVturn(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-2359
    strategy: mes 5 mins vtrun
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = VTurn(npArr, tf, tick_val=5)
    if signal == 0: return 0
    sType = "VTURN"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckObFiveMin(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2300-2330
    strategy: mes 5 mins ob
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = ObFiveMin(npArr, tf, tick_val=5)
    if signal == 0: return 0
    sType = "OB"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckThreeBarReversal(IS_EXEC_TRADE, dataDict, hourLimit, t):
    """
    tradeTime: 2230-0300
    strategy: n225mc 5 mins threeBarPlay
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    restrict = False
    if t < hourLimit * 60 + 30: restrict = True
    elif t >= (hourLimit + 2) * 60: restrict = True
    tf = '10 mins'
    if not restrict:
        npArr = dataDict[tf]
        if len(npArr) < 1: return 0
        signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=0.25)
        if signal == 0: return 0
        sType = "THREE BAR REVERSAL"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    else:
        npArr = ibc.GetDataNpArr(contractMNQ, tf)
        if len(npArr) < 1: return 0
        signalCheck, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=0.25)
        npArr = dataDict[tf]
        if len(npArr) < 1: return 0
        signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=0.25)
        if signal != 0 and signal == signalCheck:
            sType = "THREE BAR REVERSAL"
            tradeDict[tf] = [signal, op, sl, tp, sType]
            return 1
        else:
            signalTopix = 0
            signalN225 = 0
            try:
                npArrTopix = ibc.GetDataNpArr(contractMNTPX, tf)
                if len(npArrTopix) < 1: return 0
                signalTopix, op, sl, tp = ThreeBarReversal(npArrTopix, tick_val=5)
                npArr225 = ibc.GetDataNpArr(contractN225MC, tf)
                if len(npArr225) < 1: return 0
                signalN225, op, sl, tp = ThreeBarReversal(npArr225, tick_val=5)
            except: return 0
            # Check if N225 HAS Signal
            if signalTopix == 0: return 0
            if signalTopix != signalN225: return 0

            # Check if N225 AND MES, MNQ has oppisite signal
            if (
                signalTopix + signal == 0 and
                signalTopix + signalCheck == 0
            ): return 0

            if signalTopix == 1:
                if npArr[-2][2] < npArr[-3][2]: return 0
            elif npArr[-2][1] > npArr[-3][1]: return 0
            signal = signalTopix
            sType = "TOPIX & N225 THREE BAR REVERSAL"
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val=0.25)
            tradeDict[tf] = [signal, op, sl, tp, sType]
            return 1
    return 0

def CheckFvg(IS_EXEC_TRADE, dataDict, hourLimit, t):
    """
    tradeTime: 2230-0100
    strategy: mes 1 2 5 10 15 mins fvg
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tfs = ['1 min', '10 mins']
    if t >= (hourLimit + 2) * 60:
        tfs = ['10 mins']
    for tf in tfs:
        npArr = dataDict[tf]
        if len(npArr) < 1: continue
        signal, op, sl, tp = Fvg(npArr, tf, tick_val=0.25)
        if signal == 0: continue
        sType = "FVG"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1

    # 2230 - 2330
    if t < (hourLimit + 1) * 60 + 30:
        npArr = ibc.GetDataNpArr(contractQQQ, tf)
        if len(npArr) > 0:
            signal, op, sl, tp = Fvg(npArr, tf, tick_val=0.25)
            if signal != 0:
                op, sl, tp = GetOPSLTP(dataDict[tf], signal, tf, tick_val=0.25)
                sType = "QQQ FVG !"
                tradeDict[tf] = [signal, op, sl, tp, sType]
                return 1

        npArr = ibc.GetDataNpArr(contractIVV, tf)
        if len(npArr) > 0:
            signal, op, sl, tp = Fvg(npArr, tf, tick_val=0.25)
            if signal != 0:
                op, sl, tp = GetOPSLTP(dataDict[tf], signal, tf, tick_val=0.25)
                sType = "IVV FVG !"
                tradeDict[tf] = [signal, op, sl, tp, sType]
                return 1
    return 0

def CheckCombine(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-2330
    strategy: mes 5 mins threeBarPlay threeBarReversal
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp, sType = Combine(npArr, tf, tick_val=0.25)
    if signal == 0: return 0
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckThreeBarReversalSignal(IS_EXEC_TRADE, dataDict, threeBarReversalSignalContractDict):
    """
    tradeTime: 2230-2330
    strategy: etf, stock 5 mins threeBarReversal signal
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    for symbol, contract in threeBarReversalSignalContractDict.items():
        npArr = ibc.GetDataNpArr(contract, tf)
        if len(npArr) < 1: continue
        signal, op, sl, tp = ThreeBarReversal(npArr, tf)
        if signal == 0: continue
        op, sl, tp = GetOPSLTP(dataDict[tf], signal, tf, tick_val=0.25)
        sType = f"{contract.symbol} THREE BAR REVERSAL SIGNAL MES"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    return 1

def CheckFvgSignal(IS_EXEC_TRADE, dataDict, fvgSignalContractDict):
    """
    tradeTime: 2230-2330
    strategy: etf, stock 5 mins fvg signal
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    for symbol, contract in fvgSignalContractDict.items():
        npArr = ibc.GetDataNpArr(contract, tf)
        if len(npArr) < 1: continue
        signal, op, sl, tp = Fvg(npArr, tf)
        if signal == 0: continue
        op, sl, tp = GetOPSLTP(dataDict[tf], signal, tf, tick_val=0.25)
        sType = f"{contract.symbol} FVG SIGNAL MES !"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    return 1

def main():
    MIN_VOL = 1
    contract = contractMES
    hourLimit = GetTradeTime()
    dataDict = {}
    tfs = ['5 mins']
    lastOpMap = {}
    IS_EXEC_TRADE = 0
    contractSPY = Stock("SPY", 'SMART', 'USD')
    contractSPYCFD = CFD("SPY", 'SMART', 'USD')
    while(ib.sleep(3)):
        # currentTime = ib.reqCurrentTime()
        # hour = currentTime.hour
        # if hour == hourLimit + 7: continue
        for tf in tfs:
            dataDict[tf] = ibc.GetDataNpArr(contractES, tf)

        # minute = currentTime.minute
        # t = hour * 60 + minute

        IS_EXEC_TRADE = CheckSimpleMaCrossOver(IS_EXEC_TRADE, dataDict)

        for tf, res in tradeDict.items():
            signal, op, sl, tp, sType = res
            if signal != 0:
                msg = f'{sType} {contract.symbol} {tf} {signal} {op} {sl} {tp}'
                trades = ibc.GetOpenTrades()
                for trade in trades:
                    if trade.contract == contract:
                        if trade.order.action == 'BUY':
                            if signal > 0:
                                print(f'Pending BUY Order {trade.contract.symbol}')
                                continue
                        elif trade.order.action == 'SELL':
                            if signal < 0:
                                print(f'Pending SELL Order {trade.contract.symbol}')
                                continue
                if tf not in lastOpMap or op != lastOpMap[tf]:
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 5, 'USD')
                    if vol < MIN_VOL: vol = 1
                    oriOP = op
                    if vol > 1:
                        ExecTrail(ibc, signal, contract, 1, op, sl, tp, False, False, STOCKACCOUNT)
                        for i in range(2, vol + 1):
                            if op == sl: 
                                if signal == 1:
                                    sl = op - 0.25
                                else:
                                    sl = op + 0.25
                            ExecTrail(ibc, signal, contract, 1, op, sl, tp, False, False, STOCKACCOUNT)
                            if signal == 1:
                                sl += 0.25
                                tp += 100
                            else:
                                sl -= 0.25
                                tp -= 100
                    else:
                        ExecTrail(ibc, signal, contract, 1, op, sl, tp, False, False, STOCKACCOUNT)
                        npArr = ibc.GetDataNpArr(contractSPY , tf)
                        if len(npArr) > 0:
                            spyOP, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val=1)
                            vol = GetVol(stock_total_cash, spyOP, sl, tp, MIN_VOL, 1, 'USD')
                            if vol < 3: vol = 3
                            ExecTrailMOC(ibc, signal, contractSPYCFD, vol, spyOP, sl, tp, False)
                    Alert(msg)
                    lastOpMap[tf] = oriOP
                else:
                    print(msg)
        print(ACCOUNT, contract.symbol)

if __name__ == '__main__':
    main()