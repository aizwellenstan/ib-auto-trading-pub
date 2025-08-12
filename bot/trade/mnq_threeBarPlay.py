import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.threeBarPlay import ThreeBarPlay, GetOPSLTP
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade
from modules.trade.utils import GetVol

ibc = ibc.Ib()
ib = ibc.GetIB(8)

total_cash, exchangeRate = ibc.GetTotalCashExchangeRate()
print(total_cash)

def main():
    MIN_VOL = 1
    hourLimit = GetTradeTime()
    contractES, contractNQ, contractMNQ, contractMES, contractN225, contractN225M, contractN225MC, contractMNTPX, contractDJIA, contractMGC, contractQQQ = GetFuturesContracts(ib)
    tfs = ['5 mins']
    lastOpMap = {}
    while(ib.sleep(2)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        minute = currentTime.minute
        t = hour * 60 + minute
        
        if(
            t < hourLimit * 60 + 30 or
            t >= (hourLimit + 1) * 60 + 30
        ): 
            if t >= (hourLimit + 8) * 60:
                print("OUTSIDE RTH")
                print(f"START: {hourLimit}:30")
                print(f"END: {hourLimit + 8}:00")
            else:
                print("THREE BAR PLAY CLOSE POS")
            continue
        if hour == hourLimit + 7: continue
        tradeDict = {}
        for tf in tfs:
            npArr = ibc.GetDataNpArr(contractMNQ, tf)
            if len(npArr) < 1: continue
            signal, op, sl, tp = ThreeBarPlay(npArr, tf, tick_val=0.25)
            tradeDict[tf] = [signal, op, sl, tp]
            if signal != 0: break
        for tf, res in tradeDict.items():
            signal, op, sl, tp = res
            closePos = False
            if signal != 0:
                msg = f'THREE BAR PLAY {contractMNQ.symbol} {tf} {signal} {op} {sl} {tp}'
                vol = 1
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
                    print(contractMNQ.symbol, vol)
                    if vol < MIN_VOL: continue
                    ExecTrade(ibc, signal, contractMNQ, vol, op, sl, tp, closePos)
                    Alert(msg)
                    lastOpMap[tf] = op
                else:
                    print(msg)
        print(contractMNQ.symbol)

if __name__ == '__main__':
    main()