import sys 
rootPath = '../../'
sys.path.append(rootPath)
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert
import os
import pandas as pd
import numpy as np
from modules.trade.placeOrder import PlaceOrder
from ib_insync import *
from modules.csvDump import load_csv_rows
from modules.movingAverage import EmaArr, SmaArr
from modules.discord import Alert
import modules.ib as ibc

ibc = ibc.Ib()
ib = ibc.GetIB(3)

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=9)

def GetData(contract, tf):
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting=tf, whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    try:
        df = df[['open','high','low','close']]
    except: return []
    return df.to_numpy()

def execTrades(tradeList):
    for c in tradeList:
        options_contract = Option(c[0], c[1], c[2], c[3], 'SMART', tradingClass=c[0])
        print(options_contract)
        PlaceOrder(ib, options_contract)

def Strategy(npArr):
    closeArr = npArr[:,3]
    ema9 = EmaArr(closeArr, 9)
    ema21 = EmaArr(closeArr, 21)
    print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    if (
        npArr[-4][3] < npArr[-4][0] and
        npArr[-3][2] < npArr[-4][2] and
        npArr[-3][2] < npArr[-2][2] and
        npArr[-2][3] > npArr[-4][1] and
        npArr[-2][3] > npArr[-3][1] and
        ema9[-1] > ema21[-1]
    ):
        op = npArr[-1][0]
        sl = npArr[-3][2]
        tp = op + (op-sl) * 4
        return 1, op, sl, tp
    elif (
        npArr[-4][3] > npArr[-4][0] and
        npArr[-3][1] > npArr[-4][1] and
        npArr[-3][1] > npArr[-2][1] and
        npArr[-2][3] < npArr[-4][2] and
        npArr[-2][3] < npArr[-3][2] and
        ema9[-1] < ema21[-1]
    ):
        op = npArr[-1][0]
        sl = npArr[-3][1]
        tp = op - (sl-op) * 4
        return -1, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def ExecTrade(signal, contract, vol, op, sl, tp, chains=[]):
    trades = 0
    positions = ib.positions()  # A list of positions, according to IB
    if signal > 0:
        for optionschain in chains:
            strikeList = optionschain.strikes
            for strike in strikeList:
                if strike > op:
                    print(op, strike)
                    option_contract = Option(contract.symbol, optionschain.expirations[1], strike, 'C', 'SMART', tradingClass=contract.symbol)
                    ib.qualifyContracts(option_contract)
                    for position in positions:
                        if (
                            position.contract == option_contract and
                            position.position > 0
                        ): trades += 1
                    if trades < 1:
                        Alert(f'{contract.symbol} {op} {strike}')
                        res = ibc.PlaceOptionOrder(option_contract, 1)
                        if res > 0: return [option_contract]
                    else:
                        Alert(f'alerady have {signal} in {contract.symbol}')
    elif signal < 0:
        for optionschain in chains:
            strikeList = optionschain.strikes
            for strike in strikeList:
                if strike < op:
                    option_contract = Option(contract.symbol, optionschain.expirations[1], strike, 'P', 'SMART', tradingClass=contract.symbol)
                    for position in positions:
                        if (
                            position.contract == option_contract and
                            position.position < 0
                        ): trades += 1
                    if trades < 1:
                        res = ibc.PlaceOptionOrder(option_contract, 1)
                        if res > 0: return [option_contract]
                    else:
                        Alert(f'alerady have {signal} in {contract.symbol}')

def main():
    dayLightSaving = True
    if dayLightSaving:
        hourLimit = 13
    else:
        hourLimit = 14

    # positions = ib.positions()  # A list of positions, according to IB
    # for position in positions:
    #     contract = position.contract
    #     print(contract)
    # sys.exit()

    # contract = Future(conId=637533398, symbol='MES', lastTradeDateOrContractMonth='20240920', multiplier='5', currency='USD', localSymbol='MESU4', tradingClass='MES')
    # ib.qualifyContracts(contract)
    # contract = Future(conId=618688988, symbol='N225M', lastTradeDateOrContractMonth='20240912', multiplier='100', currency='JPY', localSymbol='169090019', tradingClass='225M')
    # ib.qualifyContracts(contract)
    contract = Stock('QQQ', 'SMART', 'USD')
    ib.qualifyContracts(contract)
    chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)
    
    tfs = ['5 mins', '10 mins', '15 mins', '20 mins', '30 mins', '1 hour', '2 hours', '3 hours', '4 hours', '8 hours', ]
    lastOpMap = {}
    long_option_contract = []
    short_option_contract = []
    while(ib.sleep(2)):
        for tf in tfs:
            npArr = GetData(contract, tf)
            if len(npArr) < 1: continue
            print(tf)
            signal, op, sl, tp = Strategy(npArr)
            signal = 1
            if signal != 0:
                msg = f'{contract.symbol} {tf} {signal} {op} {sl} {tp}'
                vol = 1
                trades = ibc.GetOpenTrades()
                for trade in trades:
                    if trade.order.action == 'BUY' and len(long_option_contract)>0:
                        if signal > 0:
                            print(f'Pending BUY Order {trade.contract.symbol}')
                            continue
                    elif trade.order.action == 'SELL' and len(short_option_contract)<0:
                        if signal < 0:
                            print(f'Pending SELL Order {trade.contract.symbol}')
                            continue
                if tf not in lastOpMap:
                    option_contract = ExecTrade(signal, contract, vol, op, sl, tp, chains)
                    if signal > 0:
                        long_option_contract = [option_contract]
                    elif signal < 0:
                        short_option_contract = [option_contract]
                    Alert(msg)
                    lastOpMap[tf] = op
                elif op != lastOpMap[tf]:
                    option_contract = ExecTrade(signal, contract, vol, op, sl, tp, chains)
                    if signal > 0:
                        long_option_contract = [option_contract]
                    elif signal < 0:
                        short_option_contract = [option_contract]
                    Alert(msg)
                    lastOpMap[tf] = op
                else:
                    print(msg)
                
    # trade = 0
    # while(ib.sleep(2)):
    #     currentTime = ib.reqCurrentTime()
    #     hour = currentTime.hour
    #     minute = currentTime.minute
    #     second = currentTime.second
    #     # if(hour == hourLimit and minute >= 30 and sec >= 5):
    #     #     execTrades(tradeList)
    #     #     break
    #     print(hour,minute,second)
    #     execTrades(tradeList)
    #     break

if __name__ == '__main__':
    main()