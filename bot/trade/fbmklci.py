import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
from modules.strategy.vsa import NoSupplyBar
from modules.strategy.threeBarPlay import ThreeBarPlay
from modules.strategy.harami import Harami
from modules.strategy.fvg import Fvg
from modules.strategy.fourBarTP import FourBarTP
from modules.strategy.trend import UpTrend
from modules.strategy.donchainChannel import DcBreakOut
from modules.strategy.irb import Irb, ReverseIrb
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail
from modules.trade.utils import GetVol
from ib_insync import Stock, Forex
from config import load_credentials
ACCOUNT = load_credentials('account')

ibc = ibc.Ib()
ib = ibc.GetIB(20)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
contract = Forex('MYRUSD')
ticker=ib.reqMktData(contract, '', False, False)
ib.sleep(2)
exchangeRate = ticker.bid
total_cash /= exchangeRate
total_cash *= 4 # margin
print(total_cash)
sys.exit()

contractES, contractNQ, contractMNQ, contractMES, contractN225, contractN225M, contractN225MC, contractMNTPX, contractDJIA, contractMGC, contractQQQ = GetFuturesContracts(ib)

contract1489 = Stock("1489", 'TSEJ', 'JPY')
ib.qualifyContracts(contract1489)

tradeDict = {}

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

def CheckFvg(IS_EXEC_TRADE, dataDict, hourLimit, t):
    """
    tradeTime: 2230 - 0100
    strategy: n225mc 5 mins / 10 mins / 15 mins fvg
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '2 mins'
    npArr = ibc.GetDataNpArr(contract1489, tf)
    if len(npArr) > 0:
        signal, op, sl, tp = Fvg(npArr, tf, tick_val=1)
        if signal != 0:
            op, sl, tp = GetOPSLTP(dataDict[tf], signal, tf, tick_val=1)
            sType = "1489 2min FVG"
            tradeDict[tf] = [signal, op, sl, tp, sType]
            return 1
    if(
        t >= hourLimit * 60 + 30 and
        t < (hourLimit + 3) * 60
    ): 
        tfs = ['5 mins']
        for tf in tfs:
            npArr = dataDict[tf]
            if len(npArr) < 1: continue
            signal, op, sl, tp = Fvg(npArr, tf, tick_val=1)
            if signal == 0: continue
            sType = "FVG"
            tradeDict[tf] = [signal, op, sl, tp, sType]
            return 1
    return 0

def CheckHarami(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 0900-1500 2230-0100
    strategy: n225mc 5 mins threeBarPlay
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = Harami(npArr, tf, tick_val=1)
    if signal == 0: return 0
    sType = "HARAMI"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

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

def CheckReverseIrb(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 0900-1500 2230-0100
    strategy: n225mc 5 mins threeBarPlay
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

def CheckFourBarTP(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: x0500-0600
    strategy: n225mc 5 mins 4btp
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = FourBarTP(npArr, tf, tick_val=1)
    if signal == 0: return 0
    sType = "4btp"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckNoSupplyBar(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: x 0500-0600
    strategy: n225mc 5 mins noSupplyBar
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tfs = ['5 mins', '10 mins', '15 mins']
    for tf in tfs:
        npArr = dataDict[tf]
        if len(npArr) < 1: continue
        signal, op, sl, tp = NoSupplyBar(npArr, tf, tick_val=1)
        if signal == 0: continue
        sType = "NO SUPPLY BAR"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    return 0

def CheckUpTrend(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: x 0500-0600
    strategy: n225mc 5 10 15 mins upTrend
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = UpTrend(npArr, tf, tick_val=1)
    if signal == 0: return 0
    sType = "UP TREND"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def CheckDCBreakOut(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: x 0500-0600
    strategy: n225mc 5 mins dc breakout
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '5 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = DcBreakOut(npArr, tf, tick_val=1)
    if signal == 0: return 0
    sType = "DC BREAKOUT"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

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

def CheckThreeBarReversal(IS_EXEC_TRADE):
    """
    tradeTime: x 0300-0500
    strategy: n225mc & mntpx 20 mins / 30 mins threeBarReversal
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tfs = ['20 mins', '30 mins']
    for tf in tfs:
        npArr = ibc.GetDataNpArr(contractMNTPX, tf)
        if len(npArr) < 1: continue
        signalCheck, op, sl, tp =  ThreeBarReversal(npArr, tf, tick_val=5)
        if signalCheck == 0: continue
        npArr = ibc.GetDataNpArr(contractN225MC, tf)
        if len(npArr) < 1: continue
        signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=5)
        if signal == 0: continue
        if signal != signalCheck: continue
        if signal == 1: op += 5 #one tick above topx 10.5
        sType = "n225mc & mntpx THREE BAR REVERSAL"
        tradeDict[tf] = [signal, op, sl, tp, sType]
        return 1
    return 0

def main():
    MIN_VOL = 1
    contract = contractN225MC
    hourLimit = GetTradeTime()
    dataDict = {}
    tfs = ['2 mins', '5 mins', '10 mins', '15 mins']
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

        IS_EXEC_TRADE = CheckFvg(IS_EXEC_TRADE, dataDict, hourLimit, t)
        IS_EXEC_TRADE = CheckFourBarTP(IS_EXEC_TRADE, dataDict)
        IS_EXEC_TRADE = CheckNoSupplyBar(IS_EXEC_TRADE, dataDict)
        IS_EXEC_TRADE = CheckUpTrend(IS_EXEC_TRADE, dataDict)
        IS_EXEC_TRADE = CheckDCBreakOut(IS_EXEC_TRADE, dataDict)
        # IS_EXEC_TRADE = CheckIrb(IS_EXEC_TRADE, dataDict)
        # IS_EXEC_TRADE = CheckReverseIrb(IS_EXEC_TRADE, dataDict)

        # # 2230-0300 0600-2200 
        # if(
        #     hour > (hourLimit + 7) or
        #     t < (hourLimit + 5) * 60
        # ): 
        #     IS_EXEC_TRADE = CheckMesSignalThreeBayPlayThreeBayReversal(
        #                 IS_EXEC_TRADE,
        #                 dataDict)

        if (t >= 0 and t < 6 * 60):
            IS_EXEC_TRADE = CheckHarami(IS_EXEC_TRADE, dataDict)
        else:
            print("HARAMI CLOSE POS")

        if (
            (t >= 0 and t < 6 * 60) or # Tokyo
            (t >= hourLimit * 60 + 30 and t < (hourLimit + 3) * 60) # NY 2230 - 0100
        ): 
            IS_EXEC_TRADE = CheckThreeBarPlay(IS_EXEC_TRADE, dataDict)
        else:
            print("THREE BAR PLAY CLOSE POS")

        minute = currentTime.minute
        t = hour * 60 + minute
        if(
            t < (hourLimit + 5) * 60 or
            t > (hourLimit + 7) * 60
        ): 
            IS_EXEC_TRADE = CheckThreeBarReversal(IS_EXEC_TRADE)
        
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
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 10, 'JPY')
                    if vol < MIN_VOL: 
                        Alert(msg+ f" {vol} < MIN VOL")
                        continue
                    if "!" in sType: vol = 1
                    oriOP = op
                    if vol > 1:
                        for i in range(1, vol + 1):
                            if op == sl: sl = op - 5
                            ExecTrail(ibc, signal, contract, 1, op, sl, tp, False, True, ACCOUNT)
                            op -= 5
                            sl += 5
                            tp += 100
                    else:
                        # ExecTrade(ibc, signal, contract, vol, op, sl, tp, closePos, True)
                        ExecTrail(ibc, signal, contract, 1, op, sl, tp, False, True, ACCOUNT)
                    Alert(msg)
                    lastOpMap[tf] = oriOP
                else:
                    print(msg)
        IS_EXEC_TRADE = 0
        print(contract.symbol)

if __name__ == '__main__':
    main()