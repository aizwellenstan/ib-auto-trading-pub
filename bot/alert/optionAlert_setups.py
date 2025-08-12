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

ib.connect('127.0.0.1', 7497, clientId=30)

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

def checkBuySetup(npArr):
    isBuySetup = False
    if npArr[-3][1]-npArr[-3][2] < 0.01: return False
    if(
        abs(npArr[-1][3]-npArr[-4][0])/npArr[-4][0] > 0.000815660685154947 and
        abs(npArr[-1][3]-npArr[-1][0])/npArr[-1][0] > 0.0000926527 and
        abs(npArr[-1][1]-npArr[-1][2])/abs(npArr[-2][3]-npArr[-4][0]) > 0.5921052631579616 and
        abs(npArr[-1][3]-npArr[-1][0])/(npArr[-3][1]-npArr[-3][2]) < 0.7538461538461394 and
        (not (npArr[-1][1] > npArr[-2][1] and npArr[-1][2] < npArr[-2][2])) and
        (npArr[-1][1]-npArr[-1][3])/(npArr[-1][1]-npArr[-1][2]) < 0.4382022471910116 and
        (npArr[-1][1]-npArr[-1][2])/(npArr[-2][3]-npArr[-2][2]) > 1.6000000000003032 and
        (npArr[-2][1]-npArr[-2][0])/(npArr[-2][1]-npArr[-2][2]) < 0.4791666666666556 and
        (npArr[-1][3]-npArr[-1][2])/(npArr[-1][1]-npArr[-1][2]) < 0.9000000000000178 and
        (npArr[-2][3]-npArr[-2][2])/(npArr[-2][1]-npArr[-2][2]) > 0 and
        (npArr[-4][0] - npArr[-4][3])/(npArr[-4][1] - npArr[-4][2]) > 0.16 and
        (npArr[-3][0] - npArr[-3][3])/(npArr[-3][1] - npArr[-3][2]) > 0.16 and
        (npArr[-2][0] - npArr[-2][3])/(npArr[-2][1] - npArr[-2][2]) > 0.16 and
        (npArr[-1][3] - npArr[-1][0])/(npArr[-1][1] - npArr[-1][2]) > 0.16 and
        npArr[-1][3] > npArr[-2][3] and
        npArr[-1][3] < npArr[-2][1] and
        npArr[-2][0] > npArr[-3][2] and
        npArr[-1][1] < npArr[-3][1] and
        npArr[-2][2] < npArr[-3][2] and
        (not(
            npArr[-4][0] <= npArr[-5][2] and
            npArr[-3][0] <= npArr[-4][2]
        ))
    ):
        isBuySetup = True
    return isBuySetup

def checkSellSetup(npArr):
    isSellSetup = False
    if npArr[-3][1]-npArr[-3][2] < 0.01: return False
    if(
        abs(npArr[-1][3]-npArr[-4][0])/npArr[-4][0] > 0.000815660685154947 and
        abs(npArr[-1][3]-npArr[-1][0])/npArr[-1][0] > 0.0000926527 and
        abs(npArr[-1][1]-npArr[-1][2])/abs(npArr[-2][3]-npArr[-4][0]) > 0.5921052631579616 and
        abs(npArr[-1][3]-npArr[-1][0])/(npArr[-3][1]-npArr[-3][2]) < 0.7538461538461394 and
        (not (npArr[-1][1] > npArr[-2][1] and npArr[-1][2] < npArr[-2][2])) and
        (npArr[-1][3]-npArr[-1][2])/(npArr[-1][1]-npArr[-1][2]) < 0.4382022471910116 and
        (npArr[-1][1]-npArr[-1][2])/(npArr[-2][1]-npArr[-2][3]) > 1.6000000000003032 and
        (npArr[-2][0]-npArr[-2][2])/(npArr[-2][1]-npArr[-2][2]) < 0.4791666666666556 and
        (npArr[-1][1]-npArr[-1][3])/(npArr[-1][1]-npArr[-1][2]) < 0.9000000000000178 and
        (npArr[-2][1]-npArr[-2][3])/(npArr[-2][1]-npArr[-2][2]) > 0 and
        (npArr[-4][3] - npArr[-4][0])/(npArr[-4][1] - npArr[-4][2]) > 0.16 and
        (npArr[-3][3] - npArr[-3][0])/(npArr[-3][1] - npArr[-3][2]) > 0.16 and
        (npArr[-2][3] - npArr[-2][0])/(npArr[-2][1] - npArr[-2][2]) > 0.16 and
        (npArr[-1][0] - npArr[-1][3])/(npArr[-1][1] - npArr[-1][2]) > 0.16 and
        npArr[-1][3] < npArr[-2][3] and
        npArr[-1][3] > npArr[-2][2] and
        npArr[-2][0] < npArr[-3][1] and
        npArr[-1][2] > npArr[-3][2] and
        npArr[-2][1] > npArr[-3][1] and
        (not(
            npArr[-4][0] >= npArr[-5][1] and
            npArr[-3][0] >= npArr[-4][1]
        ))
    ):
        isSellSetup = True
    return isSellSetup

def checkBull3barPlay(npArr):
    isBull3barPlay = False
    if npArr[-3][1]-npArr[-3][2] < 0.01: return False
    if abs(npArr[-2][3]-npArr[-4][0]) < 0.01: return False
    if(
        abs(npArr[-1][3]-npArr[-4][0])/npArr[-4][0] > 0.000815660685154947 and
        abs(npArr[-1][3]-npArr[-1][0])/npArr[-1][0] > 0.0000926527 and
        abs(npArr[-1][1]-npArr[-1][2])/abs(npArr[-2][3]-npArr[-4][0]) > 0.5921052631579616 and
        abs(npArr[-1][3]-npArr[-1][0])/(npArr[-3][1]-npArr[-3][2]) < 0.7538461538461394 and
        abs(npArr[-3][3]-npArr[3][0])/(npArr[-3][1]-npArr[-3][2]) < 3.5000000000000235 and
        npArr[-1][1] < npArr[-2][1] and
        npArr[-1][2] > npArr[-2][2] and
        (npArr[-1][1]-npArr[-1][2])/(npArr[-2][1]-npArr[-2][2]) < 0.46874999999999517 and
        not(
            npArr[-2][1] < npArr[-3][1] and
            npArr[-2][2] > npArr[-3][2]
        ) and
        (npArr[-2][3] - npArr[-2][0])/(npArr[-2][1] - npArr[-2][2]) > 0.16 and
        npArr[-1][3] < npArr[-3][0]
    ):
        isBull3barPlay = True
    return isBull3barPlay

def checkBear3barPlay(npArr):
    isBear3barPlay = False
    if npArr[-3][1]-npArr[-3][2] < 0.01: return False
    if abs(npArr[-2][3]-npArr[-4][0]) < 0.01: return False
    if(
        abs(npArr[-1][3]-npArr[-4][0])/npArr[-4][0] > 0.000815660685154947 and
        abs(npArr[-1][3]-npArr[-1][0])/npArr[-1][0] > 0.0000926527 and
        abs(npArr[-1][1]-npArr[-1][2])/abs(npArr[-2][3]-npArr[-4][0]) > 0.5921052631579616 and
        abs(npArr[-1][3]-npArr[-1][0])/(npArr[-3][1]-npArr[-3][2]) < 0.7538461538461394 and
        abs(npArr[-3][3]-npArr[3][0])/(npArr[-3][1]-npArr[-3][2]) < 3.5000000000000235 and
        npArr[-1][1] < npArr[-2][1] and
        npArr[-1][2] > npArr[-2][2] and
        (npArr[-1][1]-npArr[-1][2])/(npArr[-2][1]-npArr[-2][2]) < 0.46874999999999517 and
        not(
            npArr[-2][1] < npArr[-3][1] and
            npArr[-2][2] > npArr[-3][2]
        ) and
        (npArr[-2][0] - npArr[-2][3])/(npArr[-2][1] - npArr[-2][2]) > 0.16 and
        npArr[-1][3] < npArr[-3][0]
    ):
        isBear3barPlay = True
    return isBear3barPlay

def checkBull4btp(npArr):
    isBull4btp = False
    if npArr[-3][1]-npArr[-3][2] < 0.01: return False
    if abs(npArr[-4][3]-npArr[-4][0]) < 0.01: return False
    if abs(npArr[-2][3]-npArr[-4][0]) < 0.01: return False
    if(
        abs(npArr[-1][3]-npArr[-4][0])/npArr[-4][0] > 0.000815660685154947 and
        abs(npArr[-1][3]-npArr[-1][0])/npArr[-1][0] > 0.0000926527 and
        abs(npArr[-1][1]-npArr[-1][2])/abs(npArr[-2][3]-npArr[-4][0]) > 0.5921052631579616 and
        abs(npArr[-1][3]-npArr[-1][0])/(npArr[-3][1]-npArr[-3][2]) < 0.7538461538461394 and
        abs(npArr[-3][3]-npArr[-3][0])/abs(npArr[-4][3]-npArr[-4][0]) < 3 and
        (npArr[-2][1]-npArr[-2][2])/(npArr[-4][1]-npArr[-4][2]) < 2.5499999999999536 and
        not(
            npArr[-2][1] < npArr[-3][1] and
            npArr[-2][2] > npArr[-3][2]
        ) and
        (npArr[-4][0] - npArr[-4][3])/(npArr[-4][1] - npArr[-4][2]) > 0.16 and
        (npArr[-3][0] - npArr[-3][3])/(npArr[-3][1] - npArr[-3][2]) > 0.16 and
        (npArr[-2][3] - npArr[-2][0])/(npArr[-2][1] - npArr[-2][2]) > 0.16 and
        (npArr[-1][3] - npArr[-1][0])/(npArr[-1][1] - npArr[-1][2]) > 0.16 and
        (not(
            npArr[-2][3] > npArr[-4][0]
        )) and
        (not(
            npArr[-3][2] > npArr[-4][2]
        )) and
        (not(
            npArr[-2][3] > npArr[-3][3] and
            npArr[-1][3] < npArr[-3][0]
        ))
    ):
        isBull4btp = True
    return isBull4btp

def checkBear4btp(npArr):
    isBear4btp = False
    if npArr[-3][1]-npArr[-3][2] < 0.01: return False
    if abs(npArr[-4][3]-npArr[-4][0]) < 0.01: return False
    if abs(npArr[-2][3]-npArr[-4][0]) < 0.01: return False
    if(
        abs(npArr[-1][3]-npArr[-4][0])/npArr[-4][0] > 0.000815660685154947 and
        abs(npArr[-1][3]-npArr[-1][0])/npArr[-1][0] > 0.0000926527 and
        abs(npArr[-1][1]-npArr[-1][2])/abs(npArr[-2][3]-npArr[-4][0]) > 0.5921052631579616 and
        abs(npArr[-1][3]-npArr[-1][0])/(npArr[-3][1]-npArr[-3][2]) < 0.7538461538461394 and
        abs(npArr[-3][3]-npArr[-3][0])/abs(npArr[-4][3]-npArr[-4][0]) < 3 and
        (npArr[-2][1]-npArr[-2][2])/(npArr[-4][1]-npArr[-4][2]) < 2.5499999999999536 and
        not(
            npArr[-2][1] < npArr[-3][1] and
            npArr[-2][2] > npArr[-3][2]
        ) and
        (npArr[-1][1]-npArr[-1][2])/(npArr[-2][1]-npArr[-2][2]) < 0.6190476190476119 and
        (npArr[-4][3] - npArr[-4][0])/(npArr[-4][1] - npArr[-4][2]) > 0.16 and
        (npArr[-3][3] - npArr[-3][0])/(npArr[-3][1] - npArr[-3][2]) > 0.16 and
        (npArr[-2][0] - npArr[-2][3])/(npArr[-2][1] - npArr[-2][2]) > 0.16 and
        (npArr[-1][0] - npArr[-1][3])/(npArr[-1][1] - npArr[-1][2]) > 0.16 and
        (not(
            npArr[-2][3] > npArr[-4][0]
        )) and
        (not(
            npArr[-3][1] < npArr[-4][1]
        )) and
        (not(
            npArr[-2][3] < npArr[-3][3] and
            npArr[-1][3] > npArr[-3][0]
        ))
    ):
        isBear4btp = True
    return isBear4btp

def scanner(symbol):
    global fractals
    npArr = GetData(symbol)
    npArr = npArr[:-1]

    # 3bar fractals
    if (
        npArr[-1][2] > npArr[-2][2] and
        npArr[-2][2] < npArr[-3][2]
    ): 
        fractals[symbol][0][1][1] = fractals[symbol][0][1][0]
        fractals[symbol][0][1][0] = npArr[-2][2]
    if (
        npArr[-1][1] < npArr[-2][1] and
        npArr[-2][1] > npArr[-3][1]
    ):
        fractals[symbol][0][0][1] = fractals[symbol][0][0][0]
        fractals[symbol][0][0][0] = npArr[-2][1]

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
        if checkBull3barPlay(npArr):
            message = f"{symbol} bull3barPlay"
            Alert(message)
        # if checkBull4btp(npArr):
        #     message = f"{symbol} bull4btp wait 4 bko"
        #     Alert(message)
    if checkLowerHigh(npArr, fractals[symbol]):
        if checkBear3barPlay(npArr):
            message = f"{symbol} bear3barPlay"
            Alert(message)
        # if checkBear4btp(npArr):
        #     message = f"{symbol} bear4btp wait 4 bko"
        #     Alert(message)

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
    symbolList = ['QQQ', 'SPY']
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
                scanner(symbol)
            print('tick')
        if dayLightSaving:
            if(hour == 14 and minute == 49 and sec == 0):
                shutDown()
                # return
        else:
            if(hour == 15 and minute == 49 and sec == 0):
                shutDown()
                # return

if __name__ == '__main__':
    main()