import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrail, ExecTrailMOC, cancelUntriggeredAll
from modules.trade.utils import GetVol
from modules.strategy.rsi import Rsi
from config import load_credentials
ACCOUNT = load_credentials('account')
STOCKACCOUNT = load_credentials('stockAccount')

ibc = ibc.Ib()
ib = ibc.GetIB(13)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
total_cash /= 2
print(total_cash)

stock_total_cash, stock_avalible_cash = ibc.GetTotalCash(STOCKACCOUNT)
stock_total_cash /= 3

contractDict = GetFuturesContracts(ib)
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
        sl = op + tick_val * 20
        tp = op - 1540
    elif npArr[-1][1] > previousDayHigh and not IS_PREVIOUS_HIGH_BREAK:
        IS_PREVIOUS_HIGH_BREAK = True
        signal = 1
        op = previousDayHigh
        sl = op - tick_val * 20
        tp = op + 1830
    else: return 0
    sType = "PREVIOUS DAY RANGE BREAK"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def main():
    MIN_VOL = 1
    contract = contractDict["MYM"]
    tick_val = ib.reqContractDetails(contract)[0].minTick
    hourLimit = GetTradeTime()
    dataDict = {}
    tfs = ['1 min']
    lastOpMap = {}
    lastTp = 0
    lastSignal = 0
    IS_EXEC_TRADE = 0

    IS_PREVIOUS_HIGH_BREAK = False
    IS_PREVIOUS_LOW_BREAK = True

    npArr = ibc.GetDataNpArr(contractDict["YM"], '1 day', useRTH=True)
    previousDayHigh = npArr[-1][1]
    previousDayLow = npArr[-1][2]

    while(ib.sleep(2)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        if hour == hourLimit + 7: continue
        for tf in tfs:
            dataDict[tf] = ibc.GetDataNpArr(contractDict["YM"], tf)

        minute = currentTime.minute
        t = hour * 60 + minute

        # if(
        #     not IS_PREVIOUS_HIGH_BREAK or not IS_PREVIOUS_LOW_BREAK and
        #     t >= hourLimit * 60 + 30 and
        #     t < (hourLimit + 5) * 60 + 56
        # ): 
        #     IS_EXEC_TRADE = CheckPreviousDayBreak(IS_EXEC_TRADE, 
        #         IS_PREVIOUS_HIGH_BREAK, IS_PREVIOUS_LOW_BREAK, 
        #         previousDayHigh, previousDayLow,
        #         dataDict, tick_val)

        # tf = '1 min'
        # npArr = dataDict[tf]
        # if len(npArr) > 0:
        #     if npArr[-1][2] < previousDayLow: IS_PREVIOUS_LOW_BREAK = True
        #     if npArr[-1][1] > previousDayHigh: IS_PREVIOUS_HIGH_BREAK = True
        #     print(npArr[-1][1], npArr[-1][2], 
        #         previousDayHigh, previousDayLow,
        #         IS_PREVIOUS_HIGH_BREAK, IS_PREVIOUS_LOW_BREAK)
        
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
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 0.5, 'USD')
                    if vol < MIN_VOL: vol = 1
                    oriOP = op
                    fixedTrail = False
                    if sType in ["PREVIOUS DAY RANGE BREAK"]:
                        fixedTrail = True
                    if vol > 1:
                        for i in range(1, vol + 1):
                            if op == sl: 
                                if signal == 1:
                                    sl = op - tick_val
                                else:
                                    sl = op + tick_val
                            ExecTrail(ibc, signal, contract, 1, op, sl, tp, fixedTrail, ACCOUNT)
                            if signal == 1:
                                sl += tick_val
                                tp += tick_val * 400
                            else:
                                sl -= tick_val
                                tp -= tick_val * 400
                    else:
                        ibc.cancelUntriggered()
                        ExecTrail(ibc, signal, contract, 1, op, sl, tp, fixedTrail, ACCOUNT)
                    Alert(msg)
                    lastOpMap[tf] = oriOP
                else:
                    print(msg)

        IS_EXEC_TRADE = 0
        print(ACCOUNT, contract.symbol, contract.lastTradeDateOrContractMonth)

if __name__ == '__main__':
    main()