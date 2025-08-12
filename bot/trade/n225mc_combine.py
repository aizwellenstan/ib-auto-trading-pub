import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.ma import ExtremeHighLow
from modules.strategy.copula import Copula
from modules.strategy.fourBarTP import FourBarTP
from modules.strategy.kernelema import KernelEma
from modules.strategy.ob import HpOb
from modules.strategy.macd import Macd
from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
from modules.strategy.threeBarPlay import ThreeBarPlay
from modules.strategy.fvg import IFvg
from modules.strategy.vTurn import VTurn
from modules.strategy.trend import Trend
from modules.strategy.irb import HpIrb, ReverseIrb
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail, GetExtreamOp, CheckITM
from modules.trade.utils import GetVol
from ib_insync import Stock, Forex
from config import load_credentials
ACCOUNT = load_credentials('account')
if ACCOUNT == "": sys.exit()

ibc = ibc.Ib()
ib = ibc.GetIB(21)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
contract = Forex('USDJPY')
ticker=ib.reqMktData(contract, '', False, False)
ib.sleep(2)
exchangeRate = ticker.bid
total_cash *= exchangeRate
# total_cash *= 4 # margin
total_cash /= 2
print(total_cash)

contractDict = GetFuturesContracts(ib)

contract1489 = Stock("1489", 'TSEJ', 'JPY')
ib.qualifyContracts(contract1489)
print(contract1489)

tradeDict = {}

def CheckExtremeHighLow(IS_EXEC_TRADE, dataDict, tick_val):
    """
    tradeTime: 2230-0100
    strategy: n225mc 5 15 min ExtremeHighLow
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tfs = ['5 mins', '15 mins']
    for tf in tfs:
        npArr = dataDict[tf]
        if len(npArr) < 1: continue
        signal, op, sl, tp = ExtremeHighLow(npArr, tf, tick_val)
        if signal == 0: continue
        sType = "ExtremeHighLow"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    return 0

def CheckCopula(IS_EXEC_TRADE, dataDict, tick_val, t):
    """
    tradeTime: x 0500-0600
    strategy: n225 30 mins copula
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '30 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    if t >= 0 * 60 and t <= 6 * 60: 
        npArr2 = ibc.GetDataNpArr(contract1489, tf)
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
    npArr2 = ibc.GetDataNpArr(contractDict["TOPX"], tf)
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

def CheckFourBarTP(IS_EXEC_TRADE, dataDict, tick_val):
    """
    tradeTime: x 0500-0600
    strategy: n225mc 30 mins 4btp
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tfs = ['30 mins']
    for tf in tfs:
        npArr = dataDict[tf]
        if len(npArr) < 1: continue
        signal, op, sl, tp = FourBarTP(npArr, tf, tick_val)
        if signal == 0: continue
        sType = "4btp"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    return 0

def CheckKernelEma(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-2330
    strategy: mnq 5 mins kernelema
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tfs = ['5 mins', '10 mins', '15 mins']
    for tf in tfs:
        npArr = dataDict[tf]
        if len(npArr) < 1: continue
        signal, op, sl, tp = FadeRsi(npArr, tf, 5)
        if signal == 0: continue
        sType = "KERNEL EMA"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    return 0

def CheckFvg(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: x 0500-0600
    strategy: n225mc 5 mins fvg
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = HpFvg(npArr, tf, tick_val=5)
    if signal == 0: return 0
    sType = "FVG"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckHpIrb(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: x 0500-0600
    strategy: n225mc 5 mins irb
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = HpIrb(npArr, tf, tick_val=5)
    if signal == 0: return 0
    sType = "HPIRB"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckVturn(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: x 0500-0600
    strategy: n225mc 5 mins vtrun
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

def CheckOb(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: x 0500-0600
    strategy: n225mc 5 mins ob
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = HpOb(npArr, tf, tick_val=5)
    if signal == 0: return 0
    sType = "OB"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def main():
    MIN_VOL = 1
    contract = contractDict["N225MC"]
    tick_val = ib.reqContractDetails(contract)[0].minTick
    hourLimit = GetTradeTime()
    dataDict = {}
    tfs = ['5 mins', '15 mins', '30 mins']
    lastOpMap = {}
    IS_EXEC_TRADE = 0
    lastTp = 0
    lastSignal = 0
    while(ib.sleep(10)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        minute = currentTime.minute
        t = hour * 60 + minute
        if hour in [20, 21, 22]: continue # x0500-0600
        if hour == 23 and minute < 50: continue
        print(hour, minute)
        for tf in tfs:
            dataDict[tf] = ibc.GetDataNpArr(contractDict["N225"], tf)

        IS_EXEC_TRADE = CheckCopula(IS_EXEC_TRADE, dataDict, tick_val, t)

        # if(
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 5) * 60 + 30
        # ): 
        #     IS_EXEC_TRADE = CheckFourBarTP(IS_EXEC_TRADE, dataDict, tick_val)

        # IS_EXEC_TRADE = CheckTrend(IS_EXEC_TRADE, dataDict)
        # if (
        #     # (t >= 0 and t < 6 * 60) or # Tokyo FUCK ASIA
        #     (t >= hourLimit * 60 + 30 and t < hourLimit * 60 + 55) # NY 2230 - 2355
        # ): 
        #     IS_EXEC_TRADE = CheckHpIrb(IS_EXEC_TRADE, dataDict)

        # if (
        #     t >= 13 * 60 # 1630-0500 FUCK ASIA
        # ): 
        #     IS_EXEC_TRADE = CheckVturn(IS_EXEC_TRADE, dataDict)
        # IS_EXEC_TRADE = CheckOb(IS_EXEC_TRADE, dataDict)
        # IS_EXEC_TRADE = CheckMacd(IS_EXEC_TRADE, dataDict)
        # # IS_EXEC_TRADE = CheckMaCross(IS_EXEC_TRADE, dataDict)
        # # IS_EXEC_TRADE = CheckSimpleMaCross(IS_EXEC_TRADE, dataDict)
        # IS_EXEC_TRADE = CheckMaCrossHTF(IS_EXEC_TRADE, dataDict)

        # # # 2230-0300 0600-2200 
        # # if(
        # #     hour > (hourLimit + 7) or
        # #     t < (hourLimit + 5) * 60
        # # ): 
        # #     IS_EXEC_TRADE = CheckMesSignalThreeBayPlayThreeBayReversal(
        # #                 IS_EXEC_TRADE,
        # #                 dataDict)

        # if (
        #     (t >= 0 and t < 6 * 60) or # Tokyo
        #     (t >= hourLimit * 60 + 30 and t < (hourLimit + 3) * 60) # NY 2230 - 0100
        # ): 
        #     IS_EXEC_TRADE = CheckThreeBarPlay(IS_EXEC_TRADE, dataDict)
        # else:
        #     print("THREE BAR PLAY CLOSE POS")
        
        for tf, res in tradeDict.items():
            signal, op, sl, tp, sType = res
            lastSignal = signal
            lastTp = tp
            closePos = False
            positions = ibc.GetPositionsOri()  # A list of positions, according to IB
            STILL_IN_SHORT = False
            STILL_IN_LONG = False
            contractExec = contractDict["N225MC"]
            for position in positions:
                if position.contract == contract:
                    if signal > 0:
                        if position.position < 0:
                            STILL_IN_SHORT = True
                    else:
                        if position.position > 0:
                            STILL_IN_LONG = True
            if STILL_IN_SHORT or STILL_IN_LONG:
                contractExec = contractDict["N225M"]
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
                    multiplier = 10
                    if contractExec == contractDict["N225M"]:
                        multiplier = 100
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, multiplier, 'JPY')
                    if vol < MIN_VOL: vol = 1
                    if "!" in sType: vol = 1
                    oriOP = op
                    ibc.cancelUntriggered()
                    if vol > 1:
                        for i in range(1, vol + 1):
                            if signal == 1:
                                if op <= sl: 
                                    sl = op - 5
                            else:
                                if op >= sl: 
                                    sl = op + 5
                            ExecTrail(ibc, signal, contractExec, 1, op, sl, tp, tick_val, ACCOUNT)
                            if signal == 1:
                                # op -= 5
                                sl += 5
                                tp += 100
                            else:
                                # op += 5
                                sl -= 5
                                tp -= 100
                    else:
                        ExecTrail(ibc, signal, contractExec, 1, op, sl, tp, tick_val, ACCOUNT)
                    Alert(msg)
                    lastOpMap[tf] = oriOP
                else:
                    print(msg)

        if lastSignal != 0 or lastTp != 0:
            if lastSignal > 0:
                if len(dataDict['30 mins']) < 1: continue
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