import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.discord import Alert
import modules.ib as ibc
from modules.strategy.lorentizianClassification import Lz
from modules.trade.futures import GetTradeTime, GetFuturesContracts, ExecTrade, ExecTrail, ExecTrailMOC, cancelUntriggeredAll
from modules.trade.utils import GetVol
from ib_insync import Contract, Forex, CFD
from config import load_credentials
ACCOUNT = load_credentials('account')

ibc = ibc.Ib()
ib = ibc.GetIB(11)

total_cash, avalible_cash = ibc.GetTotalCash(ACCOUNT)
print(total_cash, avalible_cash)
# total_cash *= 4 # margin
total_cash /= 2
print(total_cash)

stock_total_cash, stock_avalible_cash = ibc.GetTotalCash(ACCOUNT)
stock_total_cash /= 3

tradeDict = {}

def CheckLz(IS_EXEC_TRADE, dataDict):
    """
    tradeTime: 2230-0100
    strategy: mnq 30 mins Lz
    """
    if IS_EXEC_TRADE: return 1
    global tradeDict
    tf = '30 mins'
    npArr = dataDict[tf]
    if len(npArr) < 1: return 0
    signal, op, sl, tp = Lz(npArr, tf, tick_val=1)
    if signal == 0: return 0
    sType = "LZ"
    tradeDict[tf] = [signal, op, sl, tp, sType]
    return 1

def GetEURUSDContract():
    #! [cashcontract]
    contract = Contract()
    contract.symbol = "EUR"
    contract.secType = "CFD"
    contract.currency = "USD"
    contract.exchange = "SMART"
    #! [cashcontract]
    return contract

def main():
    MIN_VOL = 1
    contract = Forex('EURUSD')
    ib.qualifyContracts(contract)
    tick_val = ib.reqContractDetails(contract)[0].minTick
    hourLimit = GetTradeTime()
    dataDict = {}
    tfs = ['30 mins']
    lastOpMap = {}
    IS_EXEC_TRADE = 0
    contractCFD = GetEURUSDContract()
    point_val = 1
    print(ib.reqContractDetails(contract)[0])
    while(ib.sleep(5)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        if hour == hourLimit + 7: continue
        for tf in tfs:
            dataDict[tf] = ibc.GetDataNpArr(contract, tf, 'ASK')
        
        IS_EXEC_TRADE = CheckLz(IS_EXEC_TRADE, dataDict)
        
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
                    vol = GetVol(total_cash, op, sl, tp, MIN_VOL, point_val, 'USD')
                    if vol < MIN_VOL: 
                        # if "IRB" not in sType: continue
                        vol = 1
                    oriOP = op
                    ExecTrail(ibc, signal, contractCFD, vol, op, sl, tp, tick_val, ACCOUNT)
                    Alert(msg)
                    lastOpMap[tf] = oriOP
                else:
                    print(msg)
        print(ACCOUNT, contract.symbol+contract.currency)

if __name__ == '__main__':
    main()