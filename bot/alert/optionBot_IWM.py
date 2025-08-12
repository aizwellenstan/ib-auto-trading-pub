import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert
import os
import pandas as pd
import numpy as np
from ib_insync import *

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=32)

def GetData(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
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
        npArr[-4][3] > npArr[-4][0]
    ):
        signal = 1
    elif (
        # (npArr[-5][3] - npArr[-5][2]) /
        # (npArr[-5][1] - npArr[-5][2]) < 0.5 and
        (npArr[-4][3] - npArr[-4][2]) /
        (npArr[-4][1] - npArr[-4][2]) < 0.5 and
        npArr[-5][3] < npArr[-5][0] and
        npArr[-4][3] < npArr[-4][0]
    ):
        signal = -1
    return signal

oldHigh = 0
oldLow = 0
def scanner(symbol, hour, minute, sec, dayLightSaving, chains, hod, lod, signal):
    global oldHigh, oldLow
    npArr = GetData(symbol)

    update = False
    if oldHigh != npArr[-1][1] and oldLow != npArr[-1][2]:
        oldHigh = npArr[-1][1]
        oldLow = npArr[-1][2]
        update = True

    if dayLightSaving:
        hourLimit = 13
    else:
        hourLimit = 14

    trade = 0
    if (
        hour == hourLimit and minute == 34
    ):
        if update:
            hod, lod = GetHodLod(npArr)
            signal = CheckSignal(npArr)
    
    if hod > 0 and lod > 0:
        if signal > 0:
            if npArr[-1][1] > hod:
                for optionschain in chains:
                    strikeList = optionschain.strikes
                    for strike in strikeList:
                        if strike > npArr[-1][3]:
                            options_contract = Option(symbol, optionschain.expirations[1], strike, 'C', 'SMART', tradingClass=symbol)
                            options_order = MarketOrder('BUY', 1,account=ib.wrapper.accounts[-1])
                            print(options_contract)
                            trade = ib.placeOrder(options_contract, options_order)
                            Alert(symbol+' QQQ 1OTM C')
                            return hod, lod, signal, 1
        elif signal < 0:
            if npArr[-1][2] < lod:
                for optionschain in chains:
                    strikeList = optionschain.strikes
                    strikeList.sort(reverse=True)
                    for strike in strikeList:
                        if strike < npArr[-1][3]:
                            options_contract = Option(symbol, optionschain.expirations[1], strike, 'P', 'SMART', tradingClass=symbol)
                            options_order = MarketOrder('BUY', 1,account=ib.wrapper.accounts[-1])
                            print(options_contract)
                            trade = ib.placeOrder(options_contract, options_order)
                            Alert(symbol+' QQQ 1OTM P')
                            return hod, lod, signal, 1
    return hod, lod, signal, 0
    
def init():
    message = "Only Trade Discord Alert!!"
    Alert(message)

def shutDown():
    message = "SHUT DOWN, GET GREEN GET OUT"
    Alert(message)
    print(message)

def main():
    dayLightSaving = True
    symbol = 'IWM'
    init()

    contract = Stock(symbol, 'SMART', 'USD')
    chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, 9579970)
    hod = 0
    lod = 0
    signal = 0
    trade = 0
    while(ib.sleep(1)):
        if trade < 1:
            hour = ib.reqCurrentTime().hour
            minute = ib.reqCurrentTime().minute
            sec = ib.reqCurrentTime().second
            hod,lod,signal,trade = scanner(symbol, hour, minute, sec, dayLightSaving, chains, hod, lod, signal)
            print('tick')
            if dayLightSaving:
                if(hour == 13 and minute == 51 and sec == 0):
                    shutDown()
            else:
                if(hour == 14 and minute == 51 and sec == 0):
                    shutDown()
        else:
            Alert(symbol+' traded')
            shutDown()
            return

if __name__ == '__main__':
    main()