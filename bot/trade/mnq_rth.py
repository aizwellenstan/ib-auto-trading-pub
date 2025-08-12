import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.threeBarReversal import ThreeBarReversal, GetOPSLTP
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade
from modules.trade.utils import GetVol

ibc = ibc.Ib()
ib = ibc.GetIB(9)

total_cash, exchangeRate = ibc.GetTotalCashExchangeRate()
print(total_cash)

def main():
    MIN_VOL = 1
    hourLimit = GetTradeTime()
    contractES, contractNQ, contractMNQ, contractMES, contractN225, contractN225M, contractN225MC, contractMNTPX, contractDJIA, contractMGC, contractQQQ = GetFuturesContracts(ib)
    tfs = ['5 mins', '10 mins']
    lastOpMap = {}
    while(ib.sleep(2)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        minute = currentTime.minute
        t = hour * 60 + minute
        restrict = False
        if t < hourLimit * 60 + 30: 
            print(hour, minute)
            restrict = True
        elif t >= (hourLimit + 2) * 60:
        # elif t >= (hourLimit + 7) * 60:
            print(hour, minute)
            restrict = True
        
        # RTH 22:30 - 06:00 JST
        # LOV VOL 03:50 - 06:00 JST
        if(
            t < hourLimit * 60 + 30 or
            # t >= (hourLimit + 7) * 60
            t >= (hourLimit + 5) * 60
        ): 
            if t >= (hourLimit + 8) * 60:
                print("OUTSIDE RTH")
                print(f"START: {hourLimit}:30")
                print(f"END: {hourLimit + 8}:00")
            else:
                print("LOW VOL")
            continue
        if hour == hourLimit + 7: continue
        if not restrict:
            tfs = ['5 mins', '10 mins']
        else:
            tfs = ['10 mins']
        tradeDict = {}
        for tf in tfs:
            if not restrict:
                npArr = ibc.GetDataNpArr(contractMNQ, tf)
                if len(npArr) < 1: continue
                signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=0.25)
                if signal == 0: 
                    if tf in ['20 mins', '30 mins']:
                        signalTopix = 0
                        signalN225 = 0
                        try:
                            npArrTopix = ibc.GetDataNpArr(contractMNTPX, tf)
                            if len(npArrTopix) > 1:
                                signalTopix, op, sl, tp = ThreeBarReversal(npArrTopix, tf, tick_val=5)
                            npArr225 = ibc.GetDataNpArr(contractN225MC, tf)
                            
                            if len(npArr225) > 1:
                                signalN225, op, sl, tp = ThreeBarReversal(npArr225, tf, tick_val=5)
                            if signalTopix != 0 and signalTopix == signalN225:
                                if signalTopix == 1:
                                    if npArr[-2][2] < npArr[-3][2]: continue
                                elif signalTopix == -1:
                                    if npArr[-2][1] > npArr[-3][1]: continue
                                signal = signalTopix
                                op, sl, tp = GetOPSLTP(npArr, signalN225, tf, tick_val=0.25)
                        except: continue
                break
            else:
                npArr = ibc.GetDataNpArr(contractMES, tf)
                if len(npArr) < 1: continue
                signalCheck, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=0.25)

                npArr = ibc.GetDataNpArr(contractMNQ, tf)
                if len(npArr) < 1: continue
                signal, op, sl, tp = ThreeBarReversal(npArr, tf, tick_val=0.25)
                
                if signal == 0 or signal != signalCheck:
                    signalTopix = 0
                    signalN225 = 0
                    try:
                        npArrTopix = ibc.GetDataNpArr(contractMNTPX, tf)
                        if len(npArrTopix) > 1:
                            signalTopix, op, sl, tp = ThreeBarReversal(npArrTopix, tf, tick_val=5)
                        npArr225 = ibc.GetDataNpArr(contractN225MC, tf)
                        if len(npArr225) > 1:
                            signalN225, op, sl, tp = ThreeBarReversal(npArr225, tf, tick_val=5)
                    except: continue
                    # Check if N225 HAS Signal
                    if signalTopix == 0: continue
                    if signalTopix != signalN225: continue

                    # Check if N225 AND MES, MNQ has oppisite signal
                    if (
                        signalTopix + signal == 0 and
                        signalTopix + signalCheck == 0
                    ): continue

                    if signalTopix == 1:
                        if npArr[-2][2] < npArr[-3][2]: continue
                    elif signalTopix == -1:
                        if npArr[-2][1] > npArr[-3][1]: continue
                    signal = signalTopix
                    op, sl, tp = GetOPSLTP(npArr, signalTopix, tf, tick_val=0.25)
            if signal != 0: 
                if signal > 0:
                    if op - sl > 141.25: sl = op - 141.25
                elif signal < 0:
                    if sl - op > 141.25: sl = op + 141.25
                tradeDict[tf] = [signal, op, sl, tp]
                break
        for tf, res in tradeDict.items():
            signal, op, sl, tp = res
            closePos = False
            if signal != 0:
                msg = f'{contractMNQ.symbol} {tf} {signal} {op} {sl} {tp}'
                trades = ibc.GetOpenTrades()
                for trade in trades:
                    if trade.contract == contractMNQ:
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
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 20, 'USD')
                    if vol < 1: continue
                    ExecTrade(ibc, signal, contractMNQ, vol, op, sl, tp, closePos)
                    Alert(msg)
                    lastOpMap[tf] = op
                else:
                    print(msg)
        print(contractMNQ.symbol)

if __name__ == '__main__':
    main()