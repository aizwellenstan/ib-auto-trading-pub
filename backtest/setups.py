import sys 
mainFolder = '../'
sys.path.append(mainFolder)
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert
from modules.ib_data import GetData, GetDfDay
import os
import pandas as pd
import numpy as np
from modules.movingAverage import EmaArr
from ib_insync import *
from modules.data import GetVolume

fractals = [
    [[0,0],[0,0]],
    [[0,0],[0,0]]
    # ,[[0,0],[0,0]]
]
hod = 0
low = 0
# secondFractalLow = 0
# firstFractalLow = 0
# secondFractalHigh = 0
# firstFractalHigh = 0

def checkVolume(symbolList):
    newSymbolList = []
    for symbol in symbolList:
        vol = GetVolume(symbol)
        print(f"{symbol} vol {vol}")
        if vol > 77834500:
            if symbol not in newSymbolList:
                newSymbolList.append(symbol)
    print(newSymbolList)
    return newSymbolList
def checkHigherLow(npArr, fractals):
    isHigherLow = False
    # if second > 0:
    #     if first > second:
    #         if npArr[-1][3] > first:
    #             isHigherLow = True
    for fractal in fractals:
        if fractal[1][1] > 0:
            if fractal[1][0] > fractal[1][1]:
                if npArr[-1][2] > fractal[1][1]:
                    isHigherLow = True
    
    return isHigherLow

def checkLowerHigh(npArr, fractals):
    isLowerHigh = False
    # if second > 0:
    #     if first < second:
    #         if npArr[-1][3] < first:
    #             isLowerHigh = True
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
        abs(npArr[-1][3]-npArr[-1][0])/(npArr[-1][1]-npArr[-1][2]) > 0.23529411764700964 and
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
        abs(npArr[-1][3]-npArr[-1][0])/(npArr[-1][1]-npArr[-1][2]) > 0.23529411764700964 and
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

def scanner(symbol, hour, minute, npArr):
    # global secondFractalLow, firstFractalLow, secondFractalHigh, firstFractalHigh
    global fractals

    # if hour == 22 and minute == 31:
    #     fractals[0][1][0] = npArr[i-1][2]
    #     fractals[0][0][0] = npArr[i-1][1]
    #     fractals[1][1][0] = npArr[i-1][2]
    #     fractals[1][0][0] = npArr[i-1][1]
    #     fractals[2][1][0] = npArr[i-1][2]
    #     fractals[2][0][0] = npArr[i-1][1]

    for i in range(5, len(npArr)+1):
        if (
            npArr[i-1][2] > npArr[i-2][2] and
            npArr[i-2][2] < npArr[i-3][2]
        ): 
            # secondFractalLow = firstFractalLow
            # firstFractalLow = npArr[i-2][2]
            fractals[0][1][1] = fractals[0][1][0]
            fractals[0][1][0] = npArr[i-2][2]
        if (
            npArr[i-1][1] < npArr[i-2][1] and
            npArr[i-2][1] > npArr[i-3][1]
        ):
            # secondFractalHigh = firstFractalHigh
            # firstFractalHigh = npArr[i-2][1]
            fractals[0][0][1] = fractals[0][0][0]
            fractals[0][0][0] = npArr[i-2][1]

        if (
            npArr[i-1][2] > npArr[i-3][2] and
            npArr[i-2][2] > npArr[i-3][2] and
            npArr[i-3][2] < npArr[i-4][2] and
            npArr[i-3][2] < npArr[i-5][2]
        ): 
            # secondFractalLow = firstFractalLow
            # firstFractalLow = npArr[i-3][2]
            fractals[1][1][1] = fractals[1][1][0]
            fractals[1][1][0] = npArr[i-3][2]
        if (
            npArr[i-1][1] < npArr[i-3][1] and
            npArr[i-2][1] < npArr[i-3][1] and
            npArr[i-3][1] > npArr[i-4][1] and
            npArr[i-3][1] > npArr[i-5][1]
        ):
            # secondFractalHigh = firstFractalHigh
            # firstFractalHigh = npArr[i-3][1]
            fractals[1][0][1] = fractals[1][0][0]
            fractals[1][0][0] = npArr[i-3][1]

        # if (
        #     npArr[i-1][2] > npArr[i-4][2] and
        #     npArr[i-2][2] > npArr[i-4][2] and
        #     npArr[i-3][2] > npArr[i-4][2] and
        #     npArr[i-5][2] < npArr[i-4][2] and
        #     npArr[i-6][2] < npArr[i-4][2] and
        #     npArr[i-7][2] < npArr[i-4][2]
        # ): 
        #     # secondFractalLow = firstFractalLow
        #     # firstFractalLow = npArr[i-3][2]
        #     fractals[2][1][1] = fractals[2][1][0]
        #     fractals[2][1][0] = npArr[i-4][2]
        # if (
        #     npArr[i-1][1] < npArr[i-4][1] and
        #     npArr[i-2][1] < npArr[i-4][1] and
        #     npArr[i-3][1] < npArr[i-4][1] and
        #     npArr[i-5][1] > npArr[i-4][1] and
        #     npArr[i-6][1] > npArr[i-4][1] and
        #     npArr[i-7][1] > npArr[i-4][1]
        # ):
        #     # secondFractalHigh = firstFractalHigh
        #     # firstFractalHigh = npArr[i-3][1]
        #     fractals[2][0][1] = fractals[2][0][0]
        #     fractals[2][0][0] = npArr[i-4][1]

    # if hour == 23 and minute == 35:
    #     print(abs(npArr[-1][3]-npArr[-1][0])/(npArr[-1][1]-npArr[-1][2]))
    #     npArr[-3][1],npArr[-4][1],npArr[-5][1])
    #     print(abs(npArr[-5][0]-npArr[-5][2])/(npArr[-5][1]-npArr[-5][2]))
    #     print(abs(npArr[-1][3]-npArr[-4][0])/npArr[-4][0])
    #     print(abs(npArr[-1][3]-npArr[-1][0])/npAr                                                 r[-1][0])
    #     print(abs(npArr[-1][1]-npArr[-1][2])/abs(npArr[-2][3]-npArr[-4][0]))
    #     print(abs(npArr[-1][3]-npArr[-1][0])/(npArr[-3][1]-npArr[-3][2]))
    #     print((npArr[-1][1]-npArr[-1][3])/(npArr[-1][1]-npArr[-1][2]))
    #     print((npArr[-1][1]-npArr[-1][2])/(npArr[-2][3]-npArr[-2][2]))
    #     print((npArr[-2][1]-npArr[-2][0])/(npArr[-2][1]-npArr[-2][2]))
    #     print((npArr[-2][3]-npArr[-2][2])/(npArr[-2][1]-npArr[-2][2]))
    #     print((npArr[-1][3]-npArr[-1][2])/(npArr[-1][1]-npArr[-1][2]))
    
    if checkHigherLow(npArr, fractals):
        if checkBuySetup(npArr):
            message = f"{symbol} buySetup"
            print(message,hour,minute)
    if checkLowerHigh(npArr, fractals):
        if checkSellSetup(npArr):
            message = f"{symbol} sellSetup"
            print(message,hour,minute)

def main():
    symbolList = [
        'QQQ',
        'SPY',
        'AMC','AAPL','AMZN','AMD','BBBY','F','NVDA',
        'WBD','DKNG','PLTR','BABA','GOOGL','CVNA','GME','SQ','MSFT',
        'COIN','INTC',
        'UPST','NKLA','CHPT','VRM','DIS','BAC','SNAP','PLUG',
'DWAC',
'RBLX',
'TAL',
'FDX',
'YETI',
'ITB',
'CVX',
'OXY',
'TGT',
'ARKK',
'NFLX',
'DLTR',
'W',
'UPS',
'MCK',
'XLF',
'ABC',
'DBC',
'FCG',
'GD',
'BMY',
'OKTA',
'GLD',
'HSY',
'FTNT',
'NVDA',
'JNPR',
'COST',
'OIH',
'ORLY',
'REGN',
'PANW',
'AVGO',
'MU',
'PAYC',
'W',
'COIN',
'SPOT',
'ZS',
'TDOC',
'UPS',
'FOXA',
'AMAT',
'FL',
'FCX',
'CSIQ',
'HPE',
'DLR',
'TLRY',
'TWTR',
'EWG',
'AAPL',
'XOM',
'EWU',
'TLT',
'V',
'C',
'FXY',
'NEE',
'AMC',
'UAA',
'CHWY',
'HOOD',
'T',
'ADBE',
'TLT',
'SI',
'NUGT',
'GM',
'KHC',
'ALB',
'MDT',
'X',
'FL',
'TRV',
'KR',
'CDNS',
'JD',
'MS',
'RIVN',
'BIDU',
'FXC',
'DD',
'IRNT',
'GMBL',
'LIDR',
    ]
    symbolList = checkVolume(symbolList)
    for symbol in symbolList:
        df = GetDfDay(symbol, 5)
        from datetime import datetime
        startDate = '2022-08-15 22:28:00'
        # endDate = '2022-08-04 05:00:00'
        df = df.loc[df['date'] >= startDate]
        # df = df.loc[df['date'] <= endDate]
        df = df.reset_index(drop=True)
        df = df.assign(hour=df['date'].dt.hour)
        df = df.assign(minute=df['date'].dt.minute)
        hour = 22
        minute = 29
        while hour <= 4 or hour >= 22:
            if hour == 4 and minute > 44: break
            # if hour == 23 and minute > 15: break
            if hour > 23:
                hour = 0
            if minute < 59:
                minute += 1
            else:
                hour += 1
                if hour == 24:
                    hour = 0
                minute = 0

            idx = df.index[(df.hour == hour) & (df.minute == minute)].tolist()
            if len(idx) > 0:
                idx = idx[0]
            else:
                continue
            df2 = df.head(idx)
            df3 = df2
            df2 = df2[['open','high','low','close']]
        
            npArr = df2.to_numpy()
            if len(npArr) < 5: continue
            scanner(symbol, hour, minute, npArr)


if __name__ == '__main__':
    main()