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
from datetime import datetime

def checkTripleTop(fractals):
    for fractal in fractals:
        if fractal[1][0] < fractal[1][1]:
            if fractal[1][1] > fractal[1][2]:
                return True
    return False

def checkTripleBottom(fractals):
    for fractal in fractals:
        if fractal[0][0] > fractal[0][1]:
            if fractal[0][1] < fractal[0][2]:
                return True
    return False

def checkSanHouUp(npArr):
    if npArr[-3][1]-npArr[-3][2] < 0.01: return False
    if (
        npArr[-1][3] > npArr[-2][1] and
        npArr[-1][3] > npArr[-3][1] and
        npArr[-1][3] > npArr[-4][1] and
        npArr[-1][3] > npArr[-5][1] and
        npArr[-1][3] > npArr[-1][0] and
        npArr[-2][3] < npArr[-2][0] and
        npArr[-3][3] > npArr[-3][0] and
        npArr[-4][3] < npArr[-4][0] and
        npArr[-5][3] > npArr[-5][0] and
        npArr[-2][3] < npArr[-5][3] and
        npArr[-3][3] < npArr[-5][3] and
        npArr[-4][3] < npArr[-5][3] and
        npArr[-5][0] < npArr[-4][2] and
        npArr[-5][0] < npArr[-3][2] and
        npArr[-5][0] < npArr[-2][2]
    ): return True
    return False

def checkSanHouDown(npArr):
    if npArr[-3][1]-npArr[-3][2] < 0.01: return False
    if (
        npArr[-1][3] < npArr[-2][2] and
        npArr[-1][3] < npArr[-3][2] and
        npArr[-1][3] < npArr[-4][2] and
        npArr[-1][3] < npArr[-5][2] and
        npArr[-1][3] < npArr[-1][0] and
        npArr[-2][3] > npArr[-2][0] and
        npArr[-3][3] < npArr[-3][0] and
        npArr[-4][3] > npArr[-4][0] and
        npArr[-5][3] < npArr[-5][0] and
        npArr[-2][3] > npArr[-5][3] and
        npArr[-3][3] > npArr[-5][3] and
        npArr[-4][3] > npArr[-5][3] and
        npArr[-5][0] > npArr[-4][1] and
        npArr[-5][0] > npArr[-3][1] and
        npArr[-5][0] > npArr[-2][1]
    ): return True
    return False



def scanner(symbol, hour, minute, npArr, fractals):
    # global secondFractalLow, firstFractalLow, secondFractalHigh, firstFractalHigh
    # global fractals
    tripleTop = 0
    tripleBottom = 0

    for i in range(5, len(npArr)+1):
        if (
            npArr[i-1][2] > npArr[i-3][2] and
            npArr[i-2][2] > npArr[i-3][2] and
            npArr[i-4][2] < npArr[i-3][2] and
            npArr[i-5][2] < npArr[i-3][2]
        ): 
            tripleTop += 1
            fractals[symbol][0][1][2] = fractals[symbol][0][1][1]
            fractals[symbol][0][1][1] = fractals[symbol][0][1][0]
            fractals[symbol][0][1][0] = npArr[i-2][2]
        if (
            npArr[i-1][1] < npArr[i-3][1] and
            npArr[i-2][1] < npArr[i-3][1] and
            npArr[i-4][1] > npArr[i-3][1] and
            npArr[i-5][1] > npArr[i-3][1]
        ):
            tripleBottom += 1
            fractals[symbol][0][0][2] = fractals[symbol][0][0][1]
            fractals[symbol][0][0][1] = fractals[symbol][0][0][0]
            fractals[symbol][0][0][0] = npArr[i-2][1]

        # if (
        #     npArr[i-1][2] > npArr[i-3][2] and
        #     npArr[i-2][2] > npArr[i-3][2] and
        #     npArr[i-3][2] < npArr[i-4][2] and
        #     npArr[i-3][2] < npArr[i-5][2]
        # ): 
        #     # secondFractalLow = firstFractalLow
        #     # firstFractalLow = npArr[i-3][2]
        #     fractals[symbol][1][1][1] = fractals[symbol][1][1][0]
        #     fractals[symbol][1][1][0] = npArr[i-3][2]
        # if (
        #     npArr[i-1][1] < npArr[i-3][1] and
        #     npArr[i-2][1] < npArr[i-3][1] and
        #     npArr[i-3][1] > npArr[i-4][1] and
        #     npArr[i-3][1] > npArr[i-5][1]
        # ):
        #     # secondFractalHigh = firstFractalHigh
        #     # firstFractalHigh = npArr[i-3][1]
        #     fractals[symbol][1][0][1] = fractals[symbol][1][0][0]
        #     fractals[symbol][1][0][0] = npArr[i-3][1]

        # if (
        #     npArr[i-1][2] > npArr[i-2][2] and
        #     npArr[i-2][2] > npArr[i-3][2] and
        #     npArr[i-3][2] > npArr[i-4][2] and
        #     npArr[i-4][2] < npArr[i-5][2] and
        #     npArr[i-5][2] < npArr[i-6][2] and
        #     npArr[i-6][2] < npArr[i-7][2]
        # ): 
        #     fractals[symbol][2][1][1] = fractals[symbol][2][1][0]
        #     fractals[symbol][2][1][0] = npArr[i-4][2]
        # if (
        #     npArr[i-1][1] < npArr[i-2][1] and
        #     npArr[i-2][1] < npArr[i-3][1] and
        #     npArr[i-3][1] < npArr[i-4][1] and
        #     npArr[i-4][1] > npArr[i-5][1] and
        #     npArr[i-5][1] > npArr[i-6][1] and
        #     npArr[i-6][1] > npArr[i-7][1]
        # ):
        #     fractals[symbol][2][0][1] = fractals[symbol][2][0][0]
        #     fractals[symbol][2][0][0] = npArr[i-4][1]

    # if hour == 22 and minute == 41:
    # #     # print((npArr[-1][1]-npArr[-1][3])/(npArr[-1][1]-npArr[-1][2]))
    # #     print((npArr[-1][3]-npArr[-1][2])/(npArr[-1][1]-npArr[-1][2]))
    #     print(abs(npArr[-2][3]-npArr[-2][0])/(npArr[-2][1]-npArr[-2][2]))
        # print(abs(npArr[-1][3]-npArr[-1][0]))
        # print((npArr[-1][1]-npArr[-1][2])/(npArr[-2][1]-npArr[-2][2]))
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
    
    # if tripleTop > 2:
    if checkSanHouUp(npArr):
        tripleTop = 0
        message = f"{symbol} SanHouUp"
        print(message,hour,minute)
    # if tripleBottom > 2:
    if checkSanHouDown(npArr):
        tripleBottom = 0
        message = f"{symbol} SanHouDown"
        print(message,hour,minute)

def main():
    global fractals
    symbolList = [
        'SPY','QQQ','DIA','IWM','XLU','XLF','XLE',
        'EWG','EWZ','EEM','VXX','UVXY',
        'TLT','TQQQ','SQQQ',
        'NVDA','SMH','MSFT','NFLX','QCOM','AMZN','TGT','AFRM',
        'AAPL','SQ','AMD','ROKU','NKE','MRVL','XBI','BA',
        'WMT','JPM','PYPL','DIS','MU','IBM','SOXL','SBUX',
        'UPST','PG','TSM','JNJ','ORCL','C','NEM','RBLX',
        'EFA','RCL','UAL','MARA','KO','INTC','WFC','FEZ',
        'CSCO','DAL','PLUG','JD','AA','HYG','PFE','FCX',
        'UBER','PINS','BAC','PARA','GOLD','LYFT','DKNG',
        'RIVN','LI','GM','WBA','CCJ','NCLH','XOM',
        'AAL','CLF','LQD','TWTR','SLB','CMCSA','RIOT','HAL',
        'QS','SOFI','CCL','M','SNAP','PLTR','F','X','HOOD',
        'CGC','CHPT','OXY','VZ','WBD','PTON','FCEL',
        'KHC','MO','KWEB','AMC','TLRY','FUBO','DVN','AVYA',
        'BP','GOEV','NKLA','BMY','JWN','ET','T','NIO','GPS',
        'BBIG','NU','SIRI','MNMD','VALE','MRO','SWN','IPOF',
        'CEI','GSAT','WEBR','PBR','BBBY',
        'BABA',
        'GOOG','GOOGL',
        'META','ARKK','GDX','SLV'
    ]
    fractals = {}
    # symbolList = checkVolume(symbolList)
    for symbol in symbolList:
        fractals[symbol] = [
            [[0,0,0],[0,0,0]],
            [[0,0,0],[0,0,0]],
            [[0,0,0],[0,0,0]]
        ]
        try:
            df = GetDfDay(symbol, 5)
            startDate = '2022-09-09 22:28:00'
            # endDate = '2022-08-04 05:00:00'
            df = df.loc[df['date'] >= startDate]
            # df = df.loc[df['date'] <= endDate]
            df = df.reset_index(drop=True)
            df = df.assign(hour=df['date'].dt.hour)
            df = df.assign(minute=df['date'].dt.minute)
        except: continue
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
            scanner(symbol, hour, minute, npArr, fractals)


if __name__ == '__main__':
    main()