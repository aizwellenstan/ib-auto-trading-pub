import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.vwap import VwapCross
from modules.strategy.threeBarReversal import ThreeBarReversalLts, GetOPSLTPLts
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
ib = ibc.GetIB(13)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
# total_cash *= 4 # margin
total_cash /= 2
print(total_cash)

stock_total_cash, stock_avalible_cash = ibc.GetTotalCash(STOCKACCOUNT)
stock_total_cash /= 3

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

# contractES, contractNQ, contractMNQ, contractMES, contractTOPX, contractMNTPX, contractMCL, contractN225, contractN225M, contractN225MC, contractMHI, contractDJIA, contractMGC,  contractJPY, contractNKD = GetFuturesContracts(ib)

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

def CheckThreeBarReversal(IS_EXEC_TRADE, dataDict, hourLimit, t):
    """
    tradeTime: 2230-0100
    strategy: 10 mins threeBarReversal
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
    return 0

def main():
    MIN_VOL = 1
    """
    IWM 2.88 100%
    BITO 5.06 100%
    XLK 2.23 80%
    EEM 1.69 66.6%
    XLU 1.53 61.5%
    """
    symbolList = ["IWM", "BITO", "XLK", "EEM", "XLU"]
    contractDict, cfdContractDict = GetContractDict(symbolList)
    hourLimit = GetTradeTime()
    dataDict = {}
    tf = "10 mins"
    lastOpMap = {}
    chainsIWM = ibc.GetChains("IWM")
    
    while(ib.sleep(2)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        if hour == hourLimit + 7: continue
        tradeDict = {}

        minute = currentTime.minute
        t = hour * 60 + minute

        if(
            t < hourLimit * 60 + 30 or
            t >= (hourLimit + 3) * 60
        ): 
            if t >= (hourLimit + 8) * 60:
                print("OUTSIDE RTH")
                print(f"START: {hourLimit}:30")
                print(f"END: {hourLimit + 8}:00")
            continue
        
        for symbol, contract in contractDict.items():
            npArr = ibc.GetDataNpArr(contract, tf)
            if len(npArr) < 1: continue
            signal, op, sl, tp = ThreeBarReversalLts(npArr, tick_val=0.01)
            print(cfdContractDict[symbol].symbol)
            if signal == 0: continue
            if op - sl < 0.3: continue
            tradeDict[symbol] = [signal, op, sl, tp]

        for symbol, res in tradeDict.items():
            signal, op, sl, tp = res
            closePos = False
            if signal != 0:
                msg = f'THREE BAR REVERSAL {cfdContractDict[symbol].symbol} {tf} {signal} {op} {sl} {tp}'
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
                if symbol not in lastOpMap or op != lastOpMap[symbol]:
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, 1, 'USD')
                    print(symbol, vol)
                    if vol < MIN_VOL: continue
                    ExecTrail(ibc, signal, cfdContractDict[symbol], vol, op, sl, tp, closePos, False, ACCOUNT)
                    if symbol == "IWM":
                        BuyOption(ib, ibc, 'IWM', chainsIWM, signal, 1, tp, CASHACCOUNT)
                    Alert(msg)
                    lastOpMap[symbol] = op
                else:
                    print(msg)
        
        # print(ACCOUNT, cfdContractDict[symbol].symbol)

if __name__ == '__main__':
    main()