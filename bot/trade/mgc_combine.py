import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.lorentizianClassification import Lz
from modules.strategy.manipulationBlock import Mb
from modules.strategy.vTurn import VTurn
from modules.strategy.ob import ObFiveMin
from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
from modules.strategy.threeBarPlay import ThreeBarPlay
from modules.strategy.irb import HpIrb
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail
from modules.trade.utils import GetVol
from ib_insync import Stock
from config import load_credentials
ACCOUNT = load_credentials('account')

ibc = ibc.Ib()
ib = ibc.GetIB(23)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
total_cash *= 4 # margin
print(total_cash)

contractES, contractNQ, contractMNQ, contractMES, contractTOPX, contractMNTPX, contractMCL, contractN225, contractN225M, contractN225MC, contractMHI, contractDJIA, contractMGC,  contractJPY, contractNKD = GetFuturesContracts(ib)

tradeDict = {}

# def CheckLz(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 2230-0100
#     strategy: mnq 30 mins Lz
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '15 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = Lz(npArr, tf, tick_val=1)
#     if signal == 0: return 0
#     sType = "LZ"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

def CheckVturn(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-2300
    strategy: mgc 5 mins vtrun
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

def CheckMb(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-2250
    strategy: mgc 5 mins mb
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = HpIrb(npArr, tf, tick_val=5)
    if signal == 0: return 0
    sType = "MB"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckObFiveMin(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-2330
    strategy: mgc 5 mins ob
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

# def CheckMesSignalThreeBayPlayThreeBayReversal(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: x 0500
#     strategy: mes 5 mins threeBayPlay threeBarReversal
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArrSignal = ibc.GetDataNpArr(contractMES, tf)
#     if len(npArrSignal) < 1: return 0
#     sType = ""
#     signal, op, sl, tp = ThreeBarReversal(npArrSignal, tf, tick_val=0.25)
#     if signal == 0: return 0 
#     sType = "THREE BAR REVERSAL MES"
#     op, sl, tp = GetOPSLTP(dataDict[tf], signal, tf, tick_val=1)
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckIrb(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 0900-1500 2230-0100
#     strategy: n225mc 5 mins threeBarPlay
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = Irb(npArr, tf, tick_val=1)
#     if signal == 0: return 0
#     sType = "IRB"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckFourBarTP(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: x0500-0600
#     strategy: n225mc 5 mins 4btp
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '5 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = FourBarTP(npArr, tf, tick_val=1)
#     if signal == 0: return 0
#     sType = "4btp"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

def CheckThreeBarPlay(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 0900-1500 2230-0100
    strategy: n225mc 5 mins threeBarPlay
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = ThreeBarPlay(npArr, tf, tick_val=1)
    if signal == 0: return 0
    sType = "THREE BAR PLAY"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def main():
    MIN_VOL = 1
    contract = contractMGC
    hourLimit = GetTradeTime()
    dataDict = {}
    tfs = ['5 mins', '15 mins']
    lastOpMap = {}
    IS_EXEC_TRADE = 0
    while(ib.sleep(2)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        minute = currentTime.minute
        t = hour * 60 + minute
        if hour in [20, 21]: continue # x0500-0600
        for tf in tfs:
            dataDict[tf] = ibc.GetDataNpArr(contract, tf)

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 3) * 60
        # ): 
        #     IS_EXEC_TRADE = CheckLz(IS_EXEC_TRADE, dataDict)

        if(
            t >= hourLimit * 60 + 30 and
            t < hourLimit * 60 + 50
        ): 
            IS_EXEC_TRADE = CheckMb(IS_EXEC_TRADE, dataDict)

        if(
            t >= hourLimit * 60 + 30 and
            t < (hourLimit + 1) * 60
        ): 
            IS_EXEC_TRADE = CheckVturn(IS_EXEC_TRADE, dataDict)
        
        for tf, res in tradeDict.items():
            signal, op, sl, tp, sType = res
            closePos = False
            if signal != 0:
                msg = f'{sType} {contract.symbol} {tf} {signal} {op} {sl} {tp}'
                trades = ibc.GetOpenTrades()
                for trade in trades:
                    if trade.contract == contract:
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
                if tf not in lastOpMap or op != lastOpMap[tf]:
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 10, 'USD')
                    if vol < MIN_VOL: continue
                    if "!" in sType: vol = 1
                    oriOP = op
                    if vol > 1:
                        for i in range(1, vol + 1):
                            if op == sl: sl = op - 0.1
                            ExecTrail(ibc, signal, contract, 1, op, sl, tp, False, True, ACCOUNT)
                            # op -= 0.1
                            sl += 0.1
                            tp += 100
                    else:
                        # ExecTrade(ibc, signal, contract, vol, op, sl, tp, closePos, True)
                        ExecTrail(ibc, signal, contract, 1, op, sl, tp, False, True, ACCOUNT)
                    Alert(msg)
                    lastOpMap[tf] = oriOP
                else:
                    print(msg)
        IS_EXEC_TRADE = 0
        print(ACCOUNT, contract.symbol)

if __name__ == '__main__':
    main()