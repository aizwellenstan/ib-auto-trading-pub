import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.kernelema import KernelEma
from modules.strategy.rsi import FadeRsi
from modules.strategy.cci import FadeCci
from modules.strategy.volume import OpeningRange
from modules.strategy.lorentizianClassification import Lz
from modules.strategy.vwap import VwapCross
from modules.strategy.irb import Irb
from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
from modules.strategy.combine import Combine
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail, ExecTrailMOC, cancelUntriggeredAll
from modules.trade.options import BuyOption
from modules.trade.utils import GetVol
from ib_insync import Stock, CFD
from config import load_credentials
ACCOUNT = load_credentials('account')
STOCKACCOUNT = load_credentials('stockAccount')
CASHACCOUNT = load_credentials('cashAccount')

ibc = ibc.Ib()
ib = ibc.GetIB(13)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
# total_cash *= 4 # margin
total_cash /= 2
print(total_cash)

stock_total_cash, stock_avalible_cash = ibc.GetTotalCash(STOCKACCOUNT)
stock_total_cash /= 3

contractES, contractNQ, contractMNQ, contractMES, contractTOPX, contractMNTPX, contractMCL, contractN225, contractN225M, contractN225MC, contractMHI, contractDJIA, contractMGC,  contractJPY, contractNKD = GetFuturesContracts(ib)
contractQQQ = Stock("QQQ", 'SMART', 'USD')
tradeDict = {}

def CheckKernelEma(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-2330
    strategy: mnq 5 mins kernelema
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tfs = ['5 mins', '10 mins', '15 mins', '20 mins']
    for tf in tfs:
        npArr = dataDict[tf]
        if len(npArr) < 1: continue
        signal, op, sl, tp = FadeRsi(npArr, tf, 5)
        if signal == 0: continue
        sType = "KERNEL EMA"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    return 0

def CheckFadeRsi(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-2330
    strategy: mnq 5 mins fade rsi
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tfs = ['5 mins', '10 mins']
    for tf in tfs:
        npArr = dataDict[tf]
        if len(npArr) < 1: continue
        signal, op, sl, tp = FadeRsi(npArr, tf, 5)
        if signal == 0: continue
        sType = "FADE RSI"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    return 0

def CheckFadeCci(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-2330
    strategy: mnq 10 mins fade cci
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '10 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = FadeCci(npArr, tf, 5)
    if signal == 0: return 0
    sType = "FADE CCI"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckOpeningRange(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2300-2331
    strategy: mnq 10 15 mins fade rsi
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tfs = ['10 mins', '15 mins']
    for tf in tfs:
        npArr = dataDict[tf]
        if len(npArr) < 1: continue
        signal, op, sl, tp = OpeningRange(npArr, tf, 5)
        if signal == 0: continue
        sType = "OPENING RANGE REVERSE"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    return 0

def CheckLz(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-0100
    strategy: mnq 30 mins Lz
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf ='30 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = Lz(npArr, tf, tick_val=1)
    if signal == 0: return 0
    sType = "LZ"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckVwapCross(IS_EXEC_TRADE, dataDict, tick_val):
    """
    tradeTime: 2230-2255
    strategy: mnq 5 mins vwap[-50:] 9 ema cross
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = VwapCross(npArr, tf, tick_val)
    if signal == 0: return 0
    sType = "9 EMA CROSS 50 VWAP"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckIrb(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-0100
    strategy: mnq 5 mins irb
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = Irb(npArr, tf, tick_val=1)
    if signal == 0: return 0
    sType = "IRB"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckThreeBarReversal(IS_EXEC_TRADE, dataDict, hourLimit, t):
    """
    tradeTime: 2230-0300
    strategy: n225mc 5 mins threeBarPlay
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '10 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=0.25)
    if signal != 0:
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

def main():
    MIN_VOL = 1
    contract = contractMNQ
    tick_val = ib.reqContractDetails(contract)[0].minTick
    hourLimit = GetTradeTime()
    dataDict = {}
    tfs = ['5 mins', '10 mins', '15 mins', '30 mins']
    lastOpMap = {}
    contractQQQCFD = CFD("QQQ", 'SMART', 'USD')
    chains = ibc.GetChains("QQQ")
    
    while(ib.sleep(2)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        if hour == hourLimit + 7: continue
        for tf in tfs:
            dataDict[tf] = ibc.GetDataNpArr(contract, tf)[:-12]

        minute = currentTime.minute
        t = hour * 60 + minute
        IS_EXEC_TRADE = 0

        # if(
        #     t == hourLimit * 60 + 34
        # ): 
        #     trades = ibc.GetOpenTrades()
        #     cancelUntriggeredAll(ibc, trades, contract)

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 1) * 60 + 30
        # ): 
        #     IS_EXEC_TRADE = CheckKernelEma(IS_EXEC_TRADE, dataDict)

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 1) * 60 + 30
        # ): 
        #     IS_EXEC_TRADE = CheckFadeRsi(IS_EXEC_TRADE, dataDict)

        if(
            t >= hourLimit * 60 + 30 and
            t < (hourLimit + 1) * 60 + 30
        ): 
            IS_EXEC_TRADE = CheckFadeCci(IS_EXEC_TRADE, dataDict)

        # if(
        #     t >= (hourLimit + 1) * 60 and
        #     t < (hourLimit + 1) * 60 + 31
        # ): 
        #     IS_EXEC_TRADE = CheckOpeningRange(IS_EXEC_TRADE, dataDict)

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 3) * 60
        # ): 
        #     IS_EXEC_TRADE = CheckLz(IS_EXEC_TRADE, dataDict)

        if(
            t >= hourLimit * 60 + 30 and
            t < (hourLimit + 3) * 60
        ): 
            IS_EXEC_TRADE = CheckThreeBarReversal(IS_EXEC_TRADE, dataDict, hourLimit, t)

        if(
            t >= hourLimit * 60 + 30 and
            t < (hourLimit + 3) * 60
        ): 
            IS_EXEC_TRADE = CheckVwapCross(IS_EXEC_TRADE, dataDict, tick_val)

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 1) * 60 + 30
        # ): 
        #     IS_EXEC_TRADE = CheckCombine(IS_EXEC_TRADE, dataDict)
        # else:
        #     print("CLOSE THREE BAR REVERSAL THREE BAR PLAY")
        
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
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 2, 'USD')
                    if vol < MIN_VOL: vol = 1
                    oriOP = op
                    # if vol > 1:
                    #     for i in range(1, vol + 1):
                    #         if op == sl: 
                    #             if signal == 1:
                    #                 sl = op - 0.25
                    #             else:
                    #                 sl = op + 0.25
                    #         ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, ACCOUNT)
                    #         if signal == 1:
                    #             # op -= 0.25
                    #             sl += 0.25
                    #             tp += 100
                    #         else:
                    #             # op += 0.25
                    #             sl -= 0.25
                    #             tp -= 100
                    # else:
                    #     ibc.cancelUntriggered()
                    #     ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, ACCOUNT)
                    #     rr = 1
                    #     if signal > 0:
                    #         rr = (tp - op) / (op - sl)
                    #     elif signal < 0:
                    #         rr = (op - tp) / (sl - op) 
                        
                    #     npArr = ibc.GetDataNpArr(contractQQQ , tf)
                    #     if len(npArr) > 0:
                    #         qqqOP, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val=1)
                    #         if signal > 0:
                    #             tp = qqqOP + (qqqOP - sl) * rr
                    #         elif signal < 0:
                    #             tp = qqqOP - (sl - qqqOP) * rr
                    #         vol = GetVol(stock_total_cash, qqqOP, sl, tp, MIN_VOL, 1, 'USD')
                    #         if vol < 12: vol = 12
                    #         ExecTrailMOC(ibc, signal, contractQQQCFD, vol, qqqOP, sl, 0.01, ACCOUNT)
                    #         BuyOption(ib, ibc, 'QQQ', chains, signal, 1, tp, CASHACCOUNT)
                    Alert(msg)
                    lastOpMap[tf] = oriOP
                else:
                    print(msg)
        print(ACCOUNT, contract.symbol)

if __name__ == '__main__':
    main()