import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
import datetime as dt
from modules.discord import Alert
import os
import pandas as pd
import numpy as np
from ib_insync import *

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=6)

def GetData(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    df = pd.DataFrame(data)
    df = df[['open','high','low','close']]
    npArr = df.to_numpy()
    
    return npArr

fractals = {}
def checkHigherLow(npArr, fractals):
    isHigherLow = False
    for fractal in fractals:
        if fractal[1][1] > 0:
            if fractal[1][0] > fractal[1][1]:
                if npArr[-1][2] > fractal[1][1]:
                    isHigherLow = True
    return isHigherLow

def checkLowerHigh(npArr, fractals):
    isLowerHigh = False
    for fractal in fractals:
        if fractal[0][1] > 0:
            if fractal[0][0] < fractal[0][1]:
                if npArr[-1][1] < fractal[0][1]:
                    isLowerHigh = True
    return isLowerHigh

def checkBuyIRB(npArr):
    isBuyIRB = False
    if npArr[-3][1]-npArr[-3][2] < 0.01: return False
    if abs(npArr[-1][3]-npArr[-1][0]) < 0.03: return False
    if abs(npArr[-1][3]-npArr[-1][0])/(npArr[-1][1]-npArr[-1][2]) < 0.1: return False
    if (npArr[-1][1]-npArr[-1][2])/(npArr[-2][1]-npArr[-2][2]) < 0.47: return False
    if (
        npArr[-3][3] > npArr[-3][0] and
        npArr[-2][3] > npArr[-2][0]
    ): return False
    if(
        (
            npArr[-1][3] > npArr[-1][0] and
            (npArr[-1][1] - npArr[-1][3]) /
            (npArr[-1][1] - npArr[-1][2]) > 0.59
        ) or
        (
            npArr[-1][3] < npArr[-1][0] and
            (npArr[-1][1] - npArr[-1][0]) /
            (npArr[-1][1] - npArr[-1][2]) > 0.59
        )
    ):
        isBuyIRB = True
    return isBuyIRB

def checkSellIRB(npArr):
    isSellIRB = False
    if npArr[-3][1]-npArr[-3][2] < 0.01: return False
    if abs(npArr[-1][3]-npArr[-1][0]) < 0.03: return False
    if abs(npArr[-1][3]-npArr[-1][0])/(npArr[-1][1]-npArr[-1][2]) < 0.1: return False
    if (npArr[-1][1]-npArr[-1][2])/(npArr[-2][1]-npArr[-2][2]) < 0.47: return False
    if (
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][3] < npArr[-2][0]
    ): return False
    if(
        (
            npArr[-1][3] < npArr[-1][0] and
            (npArr[-1][3] - npArr[-1][2]) /
            (npArr[-1][1] - npArr[-1][2]) > 0.59
        ) or
        (
            npArr[-1][3] > npArr[-1][0] and
            (npArr[-1][0] - npArr[-1][2]) /
            (npArr[-1][1] - npArr[-1][2]) > 0.59
        )
    ):
        isSellIRB = True
    return isSellIRB

def scanner(symbol):
    global fractals
    npArr = GetData(symbol)
    npArr = npArr[:-1]

    # # 3bar fractals
    # if (
    #     npArr[-1][2] > npArr[-2][2] and
    #     npArr[-2][2] < npArr[-3][2]
    # ): 
    #     fractals[symbol][0][1][1] = fractals[symbol][0][1][0]
    #     fractals[symbol][0][1][0] = npArr[-2][2]
    # if (
    #     npArr[-1][1] < npArr[-2][1] and
    #     npArr[-2][1] > npArr[-3][1]
    # ):
    #     fractals[symbol][0][0][1] = fractals[symbol][0][0][0]
    #     fractals[symbol][0][0][0] = npArr[-2][1]

    # 5bar fractals
    if (
        npArr[-1][2] > npArr[-3][2] and
        npArr[-2][2] > npArr[-3][2] and
        npArr[-3][2] < npArr[-4][2] and
        npArr[-3][2] < npArr[-5][2]
    ): 
        fractals[symbol][1][1][1] = fractals[symbol][1][1][0]
        fractals[symbol][1][1][0] = npArr[-3][2]
    if (
        npArr[-1][1] < npArr[-3][1] and
        npArr[-2][1] < npArr[-3][1] and
        npArr[-3][1] > npArr[-4][1] and
        npArr[-3][1] > npArr[-5][1]
    ):
        fractals[symbol][1][0][1] = fractals[symbol][1][0][0]
        fractals[symbol][1][0][0] = npArr[-3][1]

    if checkHigherLow(npArr, fractals[symbol]):
        if checkBuyIRB(npArr):
            message = f"{symbol} buyIRB"
            Alert(message)
    if checkLowerHigh(npArr, fractals[symbol]):
        if checkSellIRB(npArr):
            message = f"{symbol} sellIRB"
            Alert(message)

def init():
    message = "Only Trade Discord Alert!!"
    Alert(message)

def shutDown():
    message = "SHUT DOWN, GET GREEN GET OUT"
    Alert(message)
    print(message)

def main():
    global fractals
    dayLightSaving = True
    symbolList = [
        'SPY','QQQ','DIA'
    ]
    for symbol in symbolList:
        fractals[symbol] = [
            [[0,0],[0,0]],
            [[0,0],[0,0]]
        ]
    # noTrade ['WBD']
    init()
    while(ib.sleep(1)):
        hour = ib.reqCurrentTime().hour
        minute = ib.reqCurrentTime().minute
        sec = ib.reqCurrentTime().second
        if hour < 13: continue
        if hour == 13 and minute < 30: continue
        if sec == 0:
            for symbol in symbolList:
                try:
                    scanner(symbol)
                except: continue
            print('tick')
        if dayLightSaving:
            if(hour == 14 and minute == 0 and sec == 0):
                shutDown()
                return
        else:
            if(hour == 15 and minute == 0 and sec == 0):
                shutDown()
                return

if __name__ == '__main__':
    main()