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

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=6)

def GetData1d(contract):
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='1 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    df = pd.DataFrame(data)
    df = df[['open','high','low','close']]
    npArr = df.to_numpy()
    
    return npArr

def CheckPrevious(npArr):
    if (
        (npArr[-1][1] - npArr[-1][0]) /
        (npArr[-1][1] - npArr[-1][2])
    ) > 0.76: return False
    return True

def GetData(contract):
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    df = df[['open','high','low','close']]
    npArr = df.to_numpy()
    
    return npArr

def GetHodLod(npArr):
    hod = max(npArr[-2][1],npArr[-3][1],npArr[-4][1],npArr[-5][1])
    lod = min(npArr[-2][2],npArr[-3][2],npArr[-4][2],npArr[-5][2])
    return hod, lod

def CheckSignal(npArr):
    signal = 0
    if (
        # (npArr[-5][3] - npArr[-5][2]) /
        # (npArr[-5][1] - npArr[-5][2]) > 0.5 and
        (npArr[-4][3] - npArr[-4][2]) /
        (npArr[-4][1] - npArr[-4][2]) > 0.5 and
        npArr[-5][3] > npArr[-5][0] and
        npArr[-4][3] > npArr[-4][0] and
        npArr[-3][3] > npArr[-3][0]
    ):
        signal = 1
    elif (
        # (npArr[-5][3] - npArr[-5][2]) /
        # (npArr[-5][1] - npArr[-5][2]) < 0.5 and
        (npArr[-4][3] - npArr[-4][2]) /
        (npArr[-4][1] - npArr[-4][2]) < 0.5 and
        npArr[-5][3] < npArr[-5][0] and
        npArr[-4][3] < npArr[-4][0] and
        npArr[-3][3] < npArr[-3][0]
    ):
        signal = -1
    return signal

# oldHigh = 0
# oldLow = 0
def scanner(symbol, contract, hour, minute, sec, 
    hourLimit, chains, hod, lod, signal, previousClose
    ):
    # global oldHigh, oldLow
    npArr = GetData(contract)

    # update = False
    # if oldHigh != npArr[-1][1] or oldLow != npArr[-1][2]:
    #     oldHigh = npArr[-1][1]
    #     oldLow = npArr[-1][2]
    #     update = True

    trade = 0
    if (
        npArr[-1][3] < previousClose and
        hour == hourLimit and minute >= 30 and sec >= 5
    ):
        tp = (
                npArr[-1][3]
                + (previousClose-npArr[-1][3])
                * 0.51)
        for optionschain in chains:
            strikeList = optionschain.strikes
            for strike in strikeList:
                if strike > tp:
                    options_contract = Option(symbol, optionschain.expirations[1], strike, 'C', 'SMART', tradingClass=symbol)
                    PlaceOrder(ib, options_contract)
                    tp = (
                        npArr[-1][3]
                        + (previousClose-npArr[-1][3])
                        * 0.47)
                    message = symbol+' M 1OTM C TP: '+str(tp)
                    Alert(message)
                    print(message)
                    return hod, lod, signal, 1
    return hod, lod, signal, 0
    
def init():
    message = "Only Trade Discord Alert!!"
    Alert(message)

def shutDown():
    message = "SHUT DOWN, GET GREEN GET OUT"
    Alert(message)
    print(message)

def execTrades(tradeList):
    for c in tradeList:
        options_contract = Option(c[0], c[1], c[2], c[3], 'SMART', tradingClass=c[0])
        print(options_contract)
        PlaceOrder(ib, options_contract)

def main():
    dayLightSaving = True
    if dayLightSaving:
        hourLimit = 13
    else:
        hourLimit = 14

    csvPath = f"{rootPath}/data/OIChange.csv"
    tradeList = load_csv_rows(csvPath)
    print(tradeList)

    # tradeList = [
    #     ["SPY", "20230628", 437.0, 'P']
    # ]

    trade = 0
    while(ib.sleep(2)):
        currentTime = ib.reqCurrentTime()
        hour = currentTime.hour
        minute = currentTime.minute
        second = currentTime.second
        # if(hour == hourLimit and minute >= 30 and sec >= 5):
        #     execTrades(tradeList)
        #     break
        print(hour,minute,second)
        execTrades(tradeList)
        break

if __name__ == '__main__':
    main()