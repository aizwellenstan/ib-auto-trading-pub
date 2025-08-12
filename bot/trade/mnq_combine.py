import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.combine import Combine
from modules.strategy.ma import RangeBreak
from modules.strategy.threeBarReversal import GetOPSLTP
from modules.strategy.ob import Ob
from modules.strategy.copula import Copula
from modules.strategy.entropyHursts import EntropyHursts
from modules.strategy.fourBarTP import FourBarTP
from modules.strategy.kernelema import KernelEma
from modules.strategy.rsi import FadeRsi
from modules.strategy.cci import FadeCci
from modules.strategy.lorentizianClassification import Lz
from modules.strategy.vwap import VwapCross
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail, ExecTrailMOC, cancelUntriggeredAll
from modules.trade.options import BuyOption
from modules.trade.utils import GetVol
from ib_insync import Stock, CFD
from modules.trade.utils import floor_round, ceil_round
from config import load_credentials
ACCOUNT = load_credentials('account')
STOCKACCOUNT = load_credentials('stockAccount')
CASHACCOUNT = load_credentials('cashAccount')

ibc = ibc.Ib()
ib = ibc.GetIB(12)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
# total_cash *= 4 # margin
total_cash /= 2
print(total_cash)

stock_total_cash, stock_avalible_cash = ibc.GetTotalCash(STOCKACCOUNT)
stock_total_cash /= 3

contractDict = GetFuturesContracts(ib)
contractSCHD = Stock("SCHD", 'SMART', 'USD')
contractQQQ = Stock("QQQ", 'SMART', 'USD')
tradeDict = {}

def CheckPreviousDayBreak(IS_EXEC_TRADE, 
    IS_PREVIOUS_HIGH_BREAK, IS_PREVIOUS_LOW_BREAK,
    previousDayHigh, previousDayLow, 
    dataDict, tick_val):
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '1 min'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    if npArr[-1][2] < previousDayLow and not IS_PREVIOUS_LOW_BREAK:
        IS_PREVIOUS_LOW_BREAK = True
        signal = -1
        op = previousDayLow
        sl = op + tick_val * 25
        tp = op - 1030
    elif npArr[-1][1] > previousDayHigh and not IS_PREVIOUS_HIGH_BREAK:
        IS_PREVIOUS_HIGH_BREAK = True
        signal = 1
        op = previousDayHigh
        sl = op - tick_val * 25
        tp = op + 530
    else: return 0
    sType = "PREVIOUS DAY RANGE BREAK"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckCombine(IS_EXEC_TRADE, dataDict, tick_val):
    """
    tradeTime: 2230-0130
    strategy: mnq 5 mins combine
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = Combine(npArr, tf, tick_val)
    if signal == 0: return 0
    sType = "Combine"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckRangeBreak(IS_EXEC_TRADE, dataDict, tick_val):
    """
    tradeTime: 2230-2300
    strategy: mnq 5 mins reangeBreak
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = RangeBreak(npArr, tf, tick_val)
    if signal == 0: return 0
    sType = "RangeBreak"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckFvg(IS_EXEC_TRADE, dataDict, tick_val):
    """
    tradeTime: 2230-2300
    strategy: mnq 5 min fvg
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = Fvg(npArr, tf, tick_val)
    if signal == 0: return 0
    sType = "Fvg"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckCopula(IS_EXEC_TRADE, dataDict, tick_val, t, hourLimit):
    """
    tradeTime: x 0500-0600
    strategy: mnq 30 mins copula
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '30 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    if(
        t >= hourLimit * 60 + 30 and
        t <= (hourLimit + 5) * 60 + 30
    ): 
        npArr2 = ibc.GetDataNpArr(contractSCHD, tf)
        if len(npArr2) < 1: return 0
        signal, op, sl, tp = Copula(npArr, npArr2, tf, tick_val)
        if signal != 0:
            if abs(op - sl) > 1:
                if signal > 0:
                    if tp < op: return 0
                elif signal < 0:
                    if tp > op: return 0
                sType = "COPULA"
                tradeDict[tf] = [signal, op, sl, tp, sType]
                return 1
    return 0

def CheckEntropyHursts(IS_EXEC_TRADE, dataDict, tick_val):
    """
    tradeTime: 2230-2300
    strategy: mnq 5 mins EntropyHursts
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = EntropyHursts(npArr, tf, tick_val)
    if signal == 0: return 0
    sType = "EntropyHursts"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

# def CheckKernelEma(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 2230-2330
#     strategy: mnq 5 mins kernelema
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tfs = ['5 mins', '10 mins', '15 mins', '20 mins']
#     for tf in tfs:
#         npArr = dataDict[tf]
#         if len(npArr) < 1: continue
#         signal, op, sl, tp = FadeRsi(npArr, tf, 5)
#         if signal == 0: continue
#         sType = "KERNEL EMA"
#         tradeDict[tf] = [signal, op, sl, tp, sType]
#         return 1
#     return 0

# def CheckFadeRsi(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 2230-2330
#     strategy: mnq 5 mins fade rsi
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tfs = ['5 mins', '10 mins']
#     for tf in tfs:
#         npArr = dataDict[tf]
#         if len(npArr) < 1: continue
#         signal, op, sl, tp = FadeRsi(npArr, tf, 5)
#         if signal == 0: continue
#         sType = "FADE RSI"
#         tradeDict[tf] = [signal, op, sl, tp, sType]
#         return 1
#     return 0

# def CheckFadeCci(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 2230-2330
#     strategy: mnq 10 mins fade cci
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '10 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = FadeCci(npArr, tf, 5)
#     if signal == 0: return 0
#     sType = "FADE CCI"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckLz(IS_EXEC_TRADE, dataDict):
#     """
#     tradeTime: 2230-0100
#     strategy: mnq 30 mins Lz
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf ='30 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = Lz(npArr, tf, tick_val=1)
#     if signal == 0: return 0
#     sType = "LZ"
#     tradeDict[tf] = [signal, op, sl, tp, sType]
#     return 1

# def CheckThreeBarReversal(IS_EXEC_TRADE, dataDict, hourLimit, t):
#     """
#     tradeTime: 2230-0300
#     strategy: n225mc 5 mins threeBarPlay
#     """
#     if IS_EXEC_TRADE: return 1
#     global tradeDict
#     tf = '10 mins'
#     npArr = dataDict[tf]
#     if len(npArr) < 1: return 0
#     signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=0.25)
#     if signal != 0:
#         sType = "THREE BAR REVERSAL"
#         tradeDict[tf] = [signal, op, sl, tp, sType]
#         return 1
#     else:
#         signalTopix = 0
#         signalN225 = 0
#         try:
#             npArrTopix = ibc.GetDataNpArr(contractMNTPX, tf)
#             if len(npArrTopix) < 1: return 0
#             signalTopix, op, sl, tp = ThreeBarReversal(npArrTopix, tick_val=5)
#             npArr225 = ibc.GetDataNpArr(contractN225MC, tf)
#             if len(npArr225) < 1: return 0
#             signalN225, op, sl, tp = ThreeBarReversal(npArr225, tick_val=5)
#         except: return 0
#         # Check if N225 HAS Signal
#         if signalTopix == 0: return 0
#         if signalTopix != signalN225: return 0

#         # Check if N225 AND MES, MNQ has oppisite signal
#         if (
#             signalTopix + signal == 0 and
#             signalTopix + signalCheck == 0
#         ): return 0

#         if signalTopix == 1:
#             if npArr[-2][2] < npArr[-3][2]: return 0
#         elif npArr[-2][1] > npArr[-3][1]: return 0
#         signal = signalTopix
#         sType = "TOPIX & N225 THREE BAR REVERSAL"
#         op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val=0.25)
#         tradeDict[tf] = [signal, op, sl, tp, sType]
#         return 1

def main():
    MIN_VOL = 1
    contract = contractDict["MNQ"]
    tick_val = ib.reqContractDetails(contract)[0].minTick
    hourLimit = GetTradeTime()
    dataDict = {}
    tfs = ['1 min', '5 mins', '30 mins']
    lastOpMap = {}
    contractQQQCFD = CFD("QQQ", 'SMART', 'USD')
    chains = ibc.GetChains("QQQ")
    lastTp = 0
    lastSignal = 0
    IS_EXEC_TRADE = 0

    npArr = ibc.GetDataNpArr(contractDict["NQ"], '1 day', useRTH=True)
    previousDayHigh = npArr[-1][1]
    previousDayLow = npArr[-1][2]

    IS_PREVIOUS_HIGH_BREAK = True
    IS_PREVIOUS_LOW_BREAK = False

    while(ib.sleep(2)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        if hour == hourLimit + 7: continue
        for tf in tfs:
            dataDict[tf] = ibc.GetDataNpArr(contractDict["NQ"], tf)

        minute = currentTime.minute
        t = hour * 60 + minute

        if(
            (not IS_PREVIOUS_HIGH_BREAK or not IS_PREVIOUS_LOW_BREAK) and
            t >= hourLimit * 60 + 30 and
            t < (hourLimit + 5) * 60 + 56
        ): 
            IS_EXEC_TRADE = CheckPreviousDayBreak(IS_EXEC_TRADE, 
                IS_PREVIOUS_HIGH_BREAK, IS_PREVIOUS_LOW_BREAK, 
                previousDayHigh, previousDayLow,
                dataDict, tick_val)

        tf = '1 min'
        npArr = dataDict[tf]
        if len(npArr) > 0:
            if npArr[-1][2] < previousDayLow: IS_PREVIOUS_LOW_BREAK = True
            if npArr[-1][1] > previousDayHigh: IS_PREVIOUS_HIGH_BREAK = True
            print(npArr[-1][1], npArr[-1][2], 
                previousDayHigh, previousDayLow,
                IS_PREVIOUS_HIGH_BREAK, IS_PREVIOUS_LOW_BREAK)
        # if(
        #     t > hourLimit * 60 + 30 and
        #     t < (hourLimit + 1) * 60 + 15
        # ): 
        #     IS_EXEC_TRADE = CheckCombine(IS_EXEC_TRADE, dataDict, tick_val)

        if(
            t > hourLimit * 60 + 30 and
            t < (hourLimit + 1) * 60
        ): 
            IS_EXEC_TRADE = CheckRangeBreak(IS_EXEC_TRADE, dataDict, tick_val)

        if(
            t >= hourLimit * 60 + 30 and
            t <= (hourLimit + 5) * 60 + 30
        ): 
            IS_EXEC_TRADE = CheckCopula(IS_EXEC_TRADE, dataDict, tick_val, t, hourLimit)

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 1) * 60
        # ): 
        #     IS_EXEC_TRADE = CheckEntropyHursts(IS_EXEC_TRADE, dataDict, tick_val)

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 2) * 60
        # ): 
        #     IS_EXEC_TRADE = CheckFourBarTP(IS_EXEC_TRADE, dataDict, tick_val)
        
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

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 1) * 60 + 30
        # ): 
        #     IS_EXEC_TRADE = CheckFadeCci(IS_EXEC_TRADE, dataDict)

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 3) * 60
        # ): 
        #     IS_EXEC_TRADE = CheckLz(IS_EXEC_TRADE, dataDict)

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 3) * 60
        # ): 
        #     IS_EXEC_TRADE = CheckThreeBarReversal(IS_EXEC_TRADE, dataDict, hourLimit, t)

        for tf, res in tradeDict.items():
            signal, op, sl, tp, sType = res
            if signal != 0:
                lastSignal = signal
                lastTp = tp
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
                    fixedTrail = False
                    if sType in ["PREVIOUS DAY RANGE BREAK"]:
                        fixedTrail = True
                    if vol > 1:
                        for i in range(1, vol + 1):
                            if op == sl: 
                                if signal == 1:
                                    sl = op - 0.25
                                else:
                                    sl = op + 0.25
                            ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, fixedTrail, ACCOUNT)
                            if signal == 1:
                                # op -= 0.25
                                sl += 0.25
                                tp += 100
                            else:
                                # op += 0.25
                                sl -= 0.25
                                tp -= 100
                    else:
                        ibc.cancelUntriggered()
                        if signal > 0:
                            op += tick_val * 3
                        elif signal < 0:
                            op -= tick_val * 3
                        ExecTrail(ibc, signal, contract, 1, op, sl, tp, tick_val, fixedTrail, ACCOUNT)
                        RISK_ON = False
                        if sType not in [
                            "SWEEP",  
                            "EntropyHursts", "DcMidReversal", "Ob",
                            "Supertrend"]: RISK_ON = True
                        if RISK_ON:
                            rr = 1
                            if signal > 0:
                                rr = (tp - op) / (op - sl)
                            elif signal < 0:
                                rr = (op - tp) / (sl - op) 
                            
                            npArr = ibc.GetDataNpArr(contractQQQ , tf)
                            if len(npArr) > 0:
                                qqqOP, sl, qqqTP = GetOPSLTP(npArr, signal, tf, tick_val=1)
                                if signal > 0:
                                    qqqTP = qqqOP + (qqqOP - sl) * rr
                                elif signal < 0:
                                    qqqTP = qqqOP - (sl - qqqOP) * rr
                                # vol = GetVol(stock_total_cash, qqqOP, sl, qqqTP, MIN_VOL, 1, 'USD')
                                # if vol < 12: vol = 12
                                # ExecTrailMOC(ibc, signal, contractQQQCFD, vol, qqqOP, sl, 0.01, ACCOUNT)
                                if signal > 0:
                                    qqqTP = int(qqqTP) - 2
                                    strike = ceil_round(qqqOP, 1)
                                    if qqqTP < strike: qqqTP = strike
                                    # qqqTP = ceil_round(qqqOP, 1)
                                elif signal < 0:
                                    qqqTP = ceil_round(qqqTP, 1) + 2
                                    strike = int(qqqOP)
                                    if qqqTP > strike: qqqTP = strike
                                    # qqqTP = int(qqqOP)
                                try:
                                    BuyOption(ib, ibc, 'QQQ', chains, signal, 1, qqqTP, 0.26, CASHACCOUNT)
                                    if stype in ["OPENING RANGE"]:
                                        if signal > 0:
                                            qqqTP += 1
                                        elif signal < 0:
                                            qqqTP -= 1
                                        BuyOption(ib, ibc, 'QQQ', chains, signal, 1, qqqTP, 0.26, CASHACCOUNT)
                                except: pass
                    Alert(msg)
                    lastOpMap[tf] = oriOP
                else:
                    print(msg)
        if lastSignal != 0 or lastTp != 0:
            if len(dataDict['30 mins']) < 1: continue
            if lastSignal > 0:
                if dataDict['30 mins'][-1][3] > lastTp:
                    ibc.cancelUntriggered()
                    lastSignal = 0
                    lastTp = 0
            else:
                if dataDict['30 mins'][-1][3] < lastTp:
                    ibc.cancelUntriggered()
                    lastSignal = 0
                    lastTp = 0

        IS_EXEC_TRADE = 0
        print(ACCOUNT, contract.symbol, contract.lastTradeDateOrContractMonth)

if __name__ == '__main__':
    main()