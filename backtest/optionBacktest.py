import sys 
mainFolder = '../'
sys.path.append(mainFolder)
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert
from modules.ib_data import GetData, GetDf
import os
import pandas as pd
import numpy as np
from modules.movingAverage import EmaArr
from ib_insync import *

# ib = IB()

# ib.connect('127.0.0.1', 7497, clientId=4)

bar = 9
highRangeAll = 0
lowRangeAll = 0
checkPreRange = True

def scanner(symbol, hour, minute, npArr):
    global checkPreRange
    hour -= 9
    if hour < 0: hour += 24
    # npArr = GetData(symbol)

    # if (
    #     (hour == 14 and minute > 7) or
    #     hour > 14
    # ):
    # print (highRangeAll, lowRangeAll)
    # if checkPreRange:
    #     if (
    #         npArr[-1][3] > highRangeAll + 0.04
    #     ):
    #         message = "openingRangeBko buy"
    #         print(message,hour,minute)
    #         print(message)

    #     if (
    #         npArr[-1][3] < lowRangeAll - 0.04
    #     ):
    #         message = "openingRangeBko sell"
    #         print(message,hour,minute)
    #         print(message)
    
    highArrAll = np.empty(0)
    lowArrAll = np.empty(0)

    bar = 9
    for j in range(1, bar*3+1):
        highArrAll = np.append(highArrAll,npArr[-j][1])
        lowArrAll = np.append(lowArrAll,npArr[-j][2])

    if (
        (hour == 14 and minute < 9) or
        hour < 14
    ):
        if (
            npArr[-bar*2+1][3] > npArr[-bar*3][0] and
            npArr[-bar+1][3] < npArr[-bar*2][0] and
            npArr[-1][3] < npArr[-bar][0]
        ):
            lowSigArr1 = np.empty(0)
            lowSigArr2 = np.empty(0)
            
            for j in range(1, bar+1):
                lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
                lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar][2])

            if lowSigArr1.min() > lowSigArr2.min():
                op = highArrAll.max()
                sl = lowArrAll.min()
                tp = op + (op-sl) * 1.022222222
                message = f"{symbol} add buy op {op} sl {sl} tp {tp}"
                print(message,hour,minute)
        
        elif (
            npArr[-bar*2+1][3] < npArr[-bar*3][0] and
            npArr[-bar+1][3] > npArr[-bar*2][0] and
            npArr[-1][3] > npArr[-bar][0]
        ):
            highSigArr1 = np.empty(0)
            highSigArr2 = np.empty(0)
            
            for j in range(1, bar+1):
                highSigArr1 = np.append(highSigArr1,npArr[-j][1])
                highSigArr2 = np.append(highSigArr2,npArr[-j-bar][1])

            if highSigArr1.max() < highSigArr2.max():
                op = lowArrAll.min()
                sl = highArrAll.max()
                tp = op - (sl-op) * 1.022222222
                message = f"{symbol} add sell op {op} sl {sl} tp {tp}"
                print(message,hour,minute)
    # if (
    #     (hour == 14 and minute < 12) or
    #     hour < 14
    # ):
    #     bar2 = 19
    #     highSigArr1 = np.empty(0)
    #     highSigArr2 = np.empty(0)
    #     lowSigArr1 = np.empty(0)
    #     lowSigArr2 = np.empty(0)

    #     for j in range(1, bar2+1):
    #         lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
    #         lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar2][2])
    #         highSigArr1 = np.append(highSigArr1,npArr[-j][1])
    #         highSigArr2 = np.append(highSigArr2,npArr[-j-bar2][1])

    #     high1 = highSigArr1.max()
    #     high2 = highSigArr2.max()
    #     low1 = lowSigArr1.min()
    #     low2 = lowSigArr2.min()

    #     if (
    #         npArr[-bar2+1][3] < npArr[-bar2*2][0] and
    #         high1 < high2 and
    #         low1 > low2
    #     ):
    #         op = highArrAll.max()
    #         sl = lowArrAll.min()
    #         tp = op + (op-sl) * 1.022222222
    #         message = f"{symbol} 3barPlay reverse add buy op {op} sl {sl} tp {tp}"
    #         print(message,hour,minute)
    #     elif (
    #         npArr[-bar2+1][3] > npArr[-bar2*2][0] and
    #         high1 < high2 and
    #         low1 > low2
    #     ):
    #         op = lowArrAll.min()
    #         sl = highArrAll.max()
    #         tp = op - (sl-op) * 1.022222222
    #         message = f"{symbol} 3barPlay reverse add sell op {op} sl {sl} tp {tp}"
    #         print(message,hour,minute)
    
    if (
        (hour == 14 and minute < 16) or
        hour < 14
    ):
        bar3 = 13
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)

        for j in range(1, bar3+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar3][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar3*2][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar3][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar3*2][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()

        if (
            npArr[-bar3*2+1][3] < npArr[-bar3*3][0] and
            high2 < high3 and
            low2 > low3 and
            high1 < high3 and
            low1 > low3
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 4barPlay reverse add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)
        elif (
            npArr[-bar3*2+1][3] > npArr[-bar3*3][0] and
            high2 < high3 and
            low2 > low3 and
            high1 < high3 and
            low1 > low3
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 4barPlay reverse add sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

    if (
        (hour == 15 and minute < 51) or
        hour < 15
    ):
        bar8 = 25
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        highSigArr4 = np.empty(0)
        highSigArr5 = np.empty(0)
        highSigArr6 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)
        lowSigArr4 = np.empty(0)
        lowSigArr5 = np.empty(0)
        lowSigArr6 = np.empty(0)

        for j in range(1, bar8+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar8][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar8*2][2])
            lowSigArr4 = np.append(lowSigArr4,npArr[-j-bar8*3][2])
            lowSigArr5 = np.append(lowSigArr5,npArr[-j-bar8*4][2])
            lowSigArr6 = np.append(lowSigArr6,npArr[-j-bar8*5][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar8][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar8*2][1])
            highSigArr4 = np.append(highSigArr4,npArr[-j-bar8*3][1])
            highSigArr5 = np.append(highSigArr5,npArr[-j-bar8*4][1])
            highSigArr6 = np.append(highSigArr6,npArr[-j-bar8*5][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        high4 = highSigArr4.max()
        high5 = highSigArr5.max()
        high6 = highSigArr6.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()
        low4 = lowSigArr4.min()
        low5 = lowSigArr5.min()
        low6 = lowSigArr6.min()

        if (
            npArr[-bar8*5+1][3] > npArr[-bar8*6][0] and
            high5 < high6 and
            low5 > low6 and
            high4 < high6 and
            low4 > low6 and
            high3 < high6 and
            low3 > low6 and
            high2 < high6 and
            low2 > low6 and
            high1 < high6 and
            low1 > low6
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 7barPlay add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)
        elif (
            npArr[-bar8*5+1][3] < npArr[-bar8*6][0] and
            high5 < high6 and
            low5 > low6 and
            high4 < high6 and
            low4 > low6 and
            high3 < high6 and
            low3 > low6 and
            high2 < high6 and
            low2 > low6 and
            high1 < high6 and
            low1 > low6
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 7barPlay add sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

    if (
        (hour == 15 and minute < 51) or
        hour < 15
    ):
        bar9 = 26
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        highSigArr4 = np.empty(0)
        highSigArr5 = np.empty(0)
        highSigArr6 = np.empty(0)
        highSigArr7 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)
        lowSigArr4 = np.empty(0)
        lowSigArr5 = np.empty(0)
        lowSigArr6 = np.empty(0)
        lowSigArr7 = np.empty(0)

        for j in range(1, bar9+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar9][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar9*2][2])
            lowSigArr4 = np.append(lowSigArr4,npArr[-j-bar9*3][2])
            lowSigArr5 = np.append(lowSigArr5,npArr[-j-bar9*4][2])
            lowSigArr6 = np.append(lowSigArr6,npArr[-j-bar9*5][2])
            lowSigArr7 = np.append(lowSigArr7,npArr[-j-bar9*6][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar9][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar9*2][1])
            highSigArr4 = np.append(highSigArr4,npArr[-j-bar9*3][1])
            highSigArr5 = np.append(highSigArr5,npArr[-j-bar9*4][1])
            highSigArr6 = np.append(highSigArr6,npArr[-j-bar9*5][1])
            highSigArr7 = np.append(highSigArr7,npArr[-j-bar9*6][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        high4 = highSigArr4.max()
        high5 = highSigArr5.max()
        high6 = highSigArr6.max()
        high7 = highSigArr7.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()
        low4 = lowSigArr4.min()
        low5 = lowSigArr5.min()
        low6 = lowSigArr6.min()
        low7 = lowSigArr7.min()

        if (
            npArr[-bar9*6+1][3] < npArr[-bar9*7][0] and
            high6 < high7 and
            low6 > low7 and
            high5 < high7 and
            low5 > low7 and
            high4 < high7 and
            low4 > low7 and
            high3 < high7 and
            low3 > low7 and
            high2 < high7 and
            low2 > low7 and
            high1 < high7 and
            low1 > low7
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 8barPlay reverse add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)
        elif (
            npArr[-bar9*6+1][3] > npArr[-bar9*7][0] and
            high6 < high7 and
            low6 > low7 and
            high5 < high7 and
            low5 > low7 and
            high4 < high7 and
            low4 > low7 and
            high3 < high7 and
            low3 > low7 and
            high2 < high7 and
            low2 > low7 and
            high1 < high7 and
            low1 > low7
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 8barPlay reverse add sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

    if (
        (hour == 18 and minute < 9) or
        hour < 18
    ):
        bar8 = 30
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        highSigArr4 = np.empty(0)
        highSigArr5 = np.empty(0)
        highSigArr6 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)
        lowSigArr4 = np.empty(0)
        lowSigArr5 = np.empty(0)
        lowSigArr6 = np.empty(0)

        for j in range(1, bar8+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar8][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar8*2][2])
            lowSigArr4 = np.append(lowSigArr4,npArr[-j-bar8*3][2])
            lowSigArr5 = np.append(lowSigArr5,npArr[-j-bar8*4][2])
            lowSigArr6 = np.append(lowSigArr6,npArr[-j-bar8*5][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar8][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar8*2][1])
            highSigArr4 = np.append(highSigArr4,npArr[-j-bar8*3][1])
            highSigArr5 = np.append(highSigArr5,npArr[-j-bar8*4][1])
            highSigArr6 = np.append(highSigArr6,npArr[-j-bar8*5][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        high4 = highSigArr4.max()
        high5 = highSigArr5.max()
        high6 = highSigArr6.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()
        low4 = lowSigArr4.min()
        low5 = lowSigArr5.min()
        low6 = lowSigArr6.min()

        if (
            npArr[-bar8*5+1][3] < npArr[-bar8*6][0] and
            high5 < high6 and
            low5 > low6 and
            high4 < high6 and
            low4 > low6 and
            high3 < high6 and
            low3 > low6 and
            high2 < high6 and
            low2 > low6 and
            high1 < high6 and
            low1 > low6
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 7barPlay reverse add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)
        elif (
            npArr[-bar8*5+1][3] > npArr[-bar8*6][0] and
            high5 < high6 and
            low5 > low6 and
            high4 < high6 and
            low4 > low6 and
            high3 < high6 and
            low3 > low6 and
            high2 < high6 and
            low2 > low6 and
            high1 < high6 and
            low1 > low6
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 7barPlay reverse add sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

    if (
        (hour == 18 and minute < 34) or
        hour < 18
    ):
        bar9 = 21
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        highSigArr4 = np.empty(0)
        highSigArr5 = np.empty(0)
        highSigArr6 = np.empty(0)
        highSigArr7 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)
        lowSigArr4 = np.empty(0)
        lowSigArr5 = np.empty(0)
        lowSigArr6 = np.empty(0)
        lowSigArr7 = np.empty(0)

        for j in range(1, bar9+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar9][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar9*2][2])
            lowSigArr4 = np.append(lowSigArr4,npArr[-j-bar9*3][2])
            lowSigArr5 = np.append(lowSigArr5,npArr[-j-bar9*4][2])
            lowSigArr6 = np.append(lowSigArr6,npArr[-j-bar9*5][2])
            lowSigArr7 = np.append(lowSigArr7,npArr[-j-bar9*6][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar9][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar9*2][1])
            highSigArr4 = np.append(highSigArr4,npArr[-j-bar9*3][1])
            highSigArr5 = np.append(highSigArr5,npArr[-j-bar9*4][1])
            highSigArr6 = np.append(highSigArr6,npArr[-j-bar9*5][1])
            highSigArr7 = np.append(highSigArr7,npArr[-j-bar9*6][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        high4 = highSigArr4.max()
        high5 = highSigArr5.max()
        high6 = highSigArr6.max()
        high7 = highSigArr7.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()
        low4 = lowSigArr4.min()
        low5 = lowSigArr5.min()
        low6 = lowSigArr6.min()
        low7 = lowSigArr7.min()

        if (
            npArr[-bar9*6+1][3] > npArr[-bar9*7][0] and
            high6 < high7 and
            low6 > low7 and
            high5 < high7 and
            low5 > low7 and
            high4 < high7 and
            low4 > low7 and
            high3 < high7 and
            low3 > low7 and
            high2 < high7 and
            low2 > low7 and
            high1 < high7 and
            low1 > low7 and
            low1 > low2
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 8barPlay add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)
        elif (
            npArr[-bar9*6+1][3] < npArr[-bar9*7][0] and
            high6 < high7 and
            low6 > low7 and
            high5 < high7 and
            low5 > low7 and
            high4 < high7 and
            low4 > low7 and
            high3 < high7 and
            low3 > low7 and
            high2 < high7 and
            low2 > low7 and
            high1 < high7 and
            low1 > low7 and
            high1 < high2
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 8barPlay add sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

        bar10 = 26
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        highSigArr4 = np.empty(0)
        highSigArr5 = np.empty(0)
        highSigArr6 = np.empty(0)
        highSigArr7 = np.empty(0)
        highSigArr8 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)
        lowSigArr4 = np.empty(0)
        lowSigArr5 = np.empty(0)
        lowSigArr6 = np.empty(0)
        lowSigArr7 = np.empty(0)
        lowSigArr8 = np.empty(0)

        for j in range(1, bar10+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar10][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar10*2][2])
            lowSigArr4 = np.append(lowSigArr4,npArr[-j-bar10*3][2])
            lowSigArr5 = np.append(lowSigArr5,npArr[-j-bar10*4][2])
            lowSigArr6 = np.append(lowSigArr6,npArr[-j-bar10*5][2])
            lowSigArr7 = np.append(lowSigArr7,npArr[-j-bar10*6][2])
            lowSigArr8 = np.append(lowSigArr8,npArr[-j-bar10*7][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar10][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar10*2][1])
            highSigArr4 = np.append(highSigArr4,npArr[-j-bar10*3][1])
            highSigArr5 = np.append(highSigArr5,npArr[-j-bar10*4][1])
            highSigArr6 = np.append(highSigArr6,npArr[-j-bar10*5][1])
            highSigArr7 = np.append(highSigArr7,npArr[-j-bar10*6][1])
            highSigArr8 = np.append(highSigArr8,npArr[-j-bar10*7][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        high4 = highSigArr4.max()
        high5 = highSigArr5.max()
        high6 = highSigArr6.max()
        high7 = highSigArr7.max()
        high8 = highSigArr8.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()
        low4 = lowSigArr4.min()
        low5 = lowSigArr5.min()
        low6 = lowSigArr6.min()
        low7 = lowSigArr7.min()
        low8 = lowSigArr8.min()

        if (
            npArr[-bar10*7+1][3] > npArr[-bar10*8][0] and
            high7 < high8 and
            low7 > low8 and
            high6 < high8 and
            low6 > low8 and
            high5 < high8 and
            low5 > low8 and
            high4 < high8 and
            low4 > low8 and
            high3 < high8 and
            low3 > low8 and
            high2 < high8 and
            low2 > low8 and
            high1 < high8 and
            low1 > low8 and
            low1 > low2
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 9barPlay add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

        elif (
            npArr[-bar10*7+1][3] < npArr[-bar10*8][0] and
            high7 < high8 and
            low7 > low8 and
            high6 < high8 and
            low6 > low8 and
            high5 < high8 and
            low5 > low8 and
            high4 < high8 and
            low4 > low8 and
            high3 < high8 and
            low3 > low8 and
            high2 < high8 and
            low2 > low8 and
            high1 < high8 and
            low1 > low8 and
            high1 < high2
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 9barPlay add sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

        bar11 = 23
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        highSigArr4 = np.empty(0)
        highSigArr5 = np.empty(0)
        highSigArr6 = np.empty(0)
        highSigArr7 = np.empty(0)
        highSigArr8 = np.empty(0)
        highSigArr9 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)
        lowSigArr4 = np.empty(0)
        lowSigArr5 = np.empty(0)
        lowSigArr6 = np.empty(0)
        lowSigArr7 = np.empty(0)
        lowSigArr8 = np.empty(0)
        lowSigArr9 = np.empty(0)

        for j in range(1, bar11+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar11][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar11*2][2])
            lowSigArr4 = np.append(lowSigArr4,npArr[-j-bar11*3][2])
            lowSigArr5 = np.append(lowSigArr5,npArr[-j-bar11*4][2])
            lowSigArr6 = np.append(lowSigArr6,npArr[-j-bar11*5][2])
            lowSigArr7 = np.append(lowSigArr7,npArr[-j-bar11*6][2])
            lowSigArr8 = np.append(lowSigArr8,npArr[-j-bar11*7][2])
            lowSigArr9 = np.append(lowSigArr9,npArr[-j-bar11*8][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar11][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar11*2][1])
            highSigArr4 = np.append(highSigArr4,npArr[-j-bar11*3][1])
            highSigArr5 = np.append(highSigArr5,npArr[-j-bar11*4][1])
            highSigArr6 = np.append(highSigArr6,npArr[-j-bar11*5][1])
            highSigArr7 = np.append(highSigArr7,npArr[-j-bar11*6][1])
            highSigArr8 = np.append(highSigArr8,npArr[-j-bar11*7][1])
            highSigArr9 = np.append(highSigArr9,npArr[-j-bar11*8][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        high4 = highSigArr4.max()
        high5 = highSigArr5.max()
        high6 = highSigArr6.max()
        high7 = highSigArr7.max()
        high8 = highSigArr8.max()
        high9 = highSigArr9.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()
        low4 = lowSigArr4.min()
        low5 = lowSigArr5.min()
        low6 = lowSigArr6.min()
        low7 = lowSigArr7.min()
        low8 = lowSigArr8.min()
        low9 = lowSigArr9.min()

        if (
            npArr[-bar11*8+1][3] > npArr[-bar11*9][0] and
            high8 < high9 and
            low8 > low9 and
            high7 < high9 and
            low7 > low9 and
            high6 < high9 and
            low6 > low9 and
            high5 < high9 and
            low5 > low9 and
            high4 < high9 and
            low4 > low9 and
            high3 < high9 and
            low3 > low9 and
            high2 < high9 and
            low2 > low9 and
            high1 < high9 and
            low1 > low9 and
            low1 > low2
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 10barPlay add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)
        elif (
            npArr[-bar11*8+1][3] < npArr[-bar11*9][0] and
            high8 < high9 and
            low8 > low9 and
            high7 < high9 and
            low7 > low9 and
            high6 < high9 and
            low6 > low9 and
            high5 < high9 and
            low5 > low9 and
            high4 < high9 and
            low4 > low9 and
            high3 < high9 and
            low3 > low9 and
            high2 < high9 and
            low2 > low9 and
            high1 < high9 and
            low1 > low9 and
            high1 < high2
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 10barPlay add sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

    if (
        (hour == 18 and minute < 10) or
        hour < 18
    ):
        bar10 = 29
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        highSigArr4 = np.empty(0)
        highSigArr5 = np.empty(0)
        highSigArr6 = np.empty(0)
        highSigArr7 = np.empty(0)
        highSigArr8 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)
        lowSigArr4 = np.empty(0)
        lowSigArr5 = np.empty(0)
        lowSigArr6 = np.empty(0)
        lowSigArr7 = np.empty(0)
        lowSigArr8 = np.empty(0)

        for j in range(1, bar10+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar10][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar10*2][2])
            lowSigArr4 = np.append(lowSigArr4,npArr[-j-bar10*3][2])
            lowSigArr5 = np.append(lowSigArr5,npArr[-j-bar10*4][2])
            lowSigArr6 = np.append(lowSigArr6,npArr[-j-bar10*5][2])
            lowSigArr7 = np.append(lowSigArr7,npArr[-j-bar10*6][2])
            lowSigArr8 = np.append(lowSigArr8,npArr[-j-bar10*7][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar10][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar10*2][1])
            highSigArr4 = np.append(highSigArr4,npArr[-j-bar10*3][1])
            highSigArr5 = np.append(highSigArr5,npArr[-j-bar10*4][1])
            highSigArr6 = np.append(highSigArr6,npArr[-j-bar10*5][1])
            highSigArr7 = np.append(highSigArr7,npArr[-j-bar10*6][1])
            highSigArr8 = np.append(highSigArr8,npArr[-j-bar10*7][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        high4 = highSigArr4.max()
        high5 = highSigArr5.max()
        high6 = highSigArr6.max()
        high7 = highSigArr7.max()
        high8 = highSigArr8.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()
        low4 = lowSigArr4.min()
        low5 = lowSigArr5.min()
        low6 = lowSigArr6.min()
        low7 = lowSigArr7.min()
        low8 = lowSigArr8.min()

        if (
            npArr[-bar10*7+1][3] < npArr[-bar10*8][0] and
            high7 < high8 and
            low7 > low8 and
            high6 < high8 and
            low6 > low8 and
            high5 < high8 and
            low5 > low8 and
            high4 < high8 and
            low4 > low8 and
            high3 < high8 and
            low3 > low8 and
            high2 < high8 and
            low2 > low8 and
            high1 < high8 and
            low1 > low8
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 9barPlay reverse 29m add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

        elif (
            npArr[-bar10*7+1][3] > npArr[-bar10*8][0] and
            high7 < high8 and
            low7 > low8 and
            high6 < high8 and
            low6 > low8 and
            high5 < high8 and
            low5 > low8 and
            high4 < high8 and
            low4 > low8 and
            high3 < high8 and
            low3 > low8 and
            high2 < high8 and
            low2 > low8 and
            high1 < high8 and
            low1 > low8
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 9barPlay reverse add 29m sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

    if (
        (hour == 19 and minute < 43) or
        hour < 19
    ):
        bar11 = 18
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        highSigArr4 = np.empty(0)
        highSigArr5 = np.empty(0)
        highSigArr6 = np.empty(0)
        highSigArr7 = np.empty(0)
        highSigArr8 = np.empty(0)
        highSigArr9 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)
        lowSigArr4 = np.empty(0)
        lowSigArr5 = np.empty(0)
        lowSigArr6 = np.empty(0)
        lowSigArr7 = np.empty(0)
        lowSigArr8 = np.empty(0)
        lowSigArr9 = np.empty(0)

        for j in range(1, bar11+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar11][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar11*2][2])
            lowSigArr4 = np.append(lowSigArr4,npArr[-j-bar11*3][2])
            lowSigArr5 = np.append(lowSigArr5,npArr[-j-bar11*4][2])
            lowSigArr6 = np.append(lowSigArr6,npArr[-j-bar11*5][2])
            lowSigArr7 = np.append(lowSigArr7,npArr[-j-bar11*6][2])
            lowSigArr8 = np.append(lowSigArr8,npArr[-j-bar11*7][2])
            lowSigArr9 = np.append(lowSigArr9,npArr[-j-bar11*8][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar11][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar11*2][1])
            highSigArr4 = np.append(highSigArr4,npArr[-j-bar11*3][1])
            highSigArr5 = np.append(highSigArr5,npArr[-j-bar11*4][1])
            highSigArr6 = np.append(highSigArr6,npArr[-j-bar11*5][1])
            highSigArr7 = np.append(highSigArr7,npArr[-j-bar11*6][1])
            highSigArr8 = np.append(highSigArr8,npArr[-j-bar11*7][1])
            highSigArr9 = np.append(highSigArr9,npArr[-j-bar11*8][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        high4 = highSigArr4.max()
        high5 = highSigArr5.max()
        high6 = highSigArr6.max()
        high7 = highSigArr7.max()
        high8 = highSigArr8.max()
        high9 = highSigArr9.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()
        low4 = lowSigArr4.min()
        low5 = lowSigArr5.min()
        low6 = lowSigArr6.min()
        low7 = lowSigArr7.min()
        low8 = lowSigArr8.min()
        low9 = lowSigArr9.min()

        if (
            npArr[-bar11*8+1][3] < npArr[-bar11*9][0] and
            high8 < high9 and
            low8 > low9 and
            high7 < high9 and
            low7 > low9 and
            high6 < high9 and
            low6 > low9 and
            high5 < high9 and
            low5 > low9 and
            high4 < high9 and
            low4 > low9 and
            high3 < high9 and
            low3 > low9 and
            high2 < high9 and
            low2 > low9 and
            high1 < high9 and
            low1 > low9
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 10barPlay reverse add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)
        elif (
            npArr[-bar11*8+1][3] > npArr[-bar11*9][0] and
            high8 < high9 and
            low8 > low9 and
            high7 < high9 and
            low7 > low9 and
            high6 < high9 and
            low6 > low9 and
            high5 < high9 and
            low5 > low9 and
            high4 < high9 and
            low4 > low9 and
            high3 < high9 and
            low3 > low9 and
            high2 < high9 and
            low2 > low9 and
            high1 < high9 and
            low1 > low9
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 10barPlay reverse add sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

        bar = 16
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        highSigArr4 = np.empty(0)
        highSigArr5 = np.empty(0)
        highSigArr6 = np.empty(0)
        highSigArr7 = np.empty(0)
        highSigArr8 = np.empty(0)
        highSigArr9 = np.empty(0)
        highSigArr10 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)
        lowSigArr4 = np.empty(0)
        lowSigArr5 = np.empty(0)
        lowSigArr6 = np.empty(0)
        lowSigArr7 = np.empty(0)
        lowSigArr8 = np.empty(0)
        lowSigArr9 = np.empty(0)
        lowSigArr10 = np.empty(0)

        for j in range(1, bar+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar*2][2])
            lowSigArr4 = np.append(lowSigArr4,npArr[-j-bar*3][2])
            lowSigArr5 = np.append(lowSigArr5,npArr[-j-bar*4][2])
            lowSigArr6 = np.append(lowSigArr6,npArr[-j-bar*5][2])
            lowSigArr7 = np.append(lowSigArr7,npArr[-j-bar*6][2])
            lowSigArr8 = np.append(lowSigArr8,npArr[-j-bar*7][2])
            lowSigArr9 = np.append(lowSigArr9,npArr[-j-bar*8][2])
            lowSigArr10 = np.append(lowSigArr10,npArr[-j-bar*9][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar*2][1])
            highSigArr4 = np.append(highSigArr4,npArr[-j-bar*3][1])
            highSigArr5 = np.append(highSigArr5,npArr[-j-bar*4][1])
            highSigArr6 = np.append(highSigArr6,npArr[-j-bar*5][1])
            highSigArr7 = np.append(highSigArr7,npArr[-j-bar*6][1])
            highSigArr8 = np.append(highSigArr8,npArr[-j-bar*7][1])
            highSigArr9 = np.append(highSigArr9,npArr[-j-bar*8][1])
            highSigArr10 = np.append(highSigArr10,npArr[-j-bar*9][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        high4 = highSigArr4.max()
        high5 = highSigArr5.max()
        high6 = highSigArr6.max()
        high7 = highSigArr7.max()
        high8 = highSigArr8.max()
        high9 = highSigArr9.max()
        high10 = highSigArr10.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()
        low4 = lowSigArr4.min()
        low5 = lowSigArr5.min()
        low6 = lowSigArr6.min()
        low7 = lowSigArr7.min()
        low8 = lowSigArr8.min()
        low9 = lowSigArr9.min()
        low10 = lowSigArr10.min()

        if (
            npArr[-bar*9+1][3] < npArr[-bar*10][0] and
            high9 < high10 and
            low9 > low10 and
            high8 < high10 and
            low8 > low10 and
            high7 < high10 and
            low7 > low10 and
            high6 < high10 and
            low6 > low10 and
            high5 < high10 and
            low5 > low10 and
            high4 < high10 and
            low4 > low10 and
            high3 < high10 and
            low3 > low10 and
            high2 < high10 and
            low2 > low10 and
            high1 < high10 and
            low1 > low10
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 11barPlay reverse add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)
        elif (
            npArr[-bar*9+1][3] > npArr[-bar*10][0] and
            high9 < high10 and
            low9 > low10 and
            high8 < high10 and
            low8 > low10 and
            high7 < high10 and
            low7 > low10 and
            high6 < high10 and
            low6 > low10 and
            high5 < high10 and
            low5 > low10 and
            high4 < high10 and
            low4 > low10 and
            high3 < high10 and
            low3 > low10 and
            high2 < high10 and
            low2 > low10 and
            high1 < high10 and
            low1 > low10
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 11barPlay reverse add sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

        bar = 14
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        highSigArr3 = np.empty(0)
        highSigArr4 = np.empty(0)
        highSigArr5 = np.empty(0)
        highSigArr6 = np.empty(0)
        highSigArr7 = np.empty(0)
        highSigArr8 = np.empty(0)
        highSigArr9 = np.empty(0)
        highSigArr10 = np.empty(0)
        highSigArr11 = np.empty(0)
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)
        lowSigArr3 = np.empty(0)
        lowSigArr4 = np.empty(0)
        lowSigArr5 = np.empty(0)
        lowSigArr6 = np.empty(0)
        lowSigArr7 = np.empty(0)
        lowSigArr8 = np.empty(0)
        lowSigArr9 = np.empty(0)
        lowSigArr10 = np.empty(0)
        lowSigArr11 = np.empty(0)

        for j in range(1, bar+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar][2])
            lowSigArr3 = np.append(lowSigArr3,npArr[-j-bar*2][2])
            lowSigArr4 = np.append(lowSigArr4,npArr[-j-bar*3][2])
            lowSigArr5 = np.append(lowSigArr5,npArr[-j-bar*4][2])
            lowSigArr6 = np.append(lowSigArr6,npArr[-j-bar*5][2])
            lowSigArr7 = np.append(lowSigArr7,npArr[-j-bar*6][2])
            lowSigArr8 = np.append(lowSigArr8,npArr[-j-bar*7][2])
            lowSigArr9 = np.append(lowSigArr9,npArr[-j-bar*8][2])
            lowSigArr10 = np.append(lowSigArr10,npArr[-j-bar*9][2])
            lowSigArr11 = np.append(lowSigArr11,npArr[-j-bar*10][2])
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar][1])
            highSigArr3 = np.append(highSigArr3,npArr[-j-bar*2][1])
            highSigArr4 = np.append(highSigArr4,npArr[-j-bar*3][1])
            highSigArr5 = np.append(highSigArr5,npArr[-j-bar*4][1])
            highSigArr6 = np.append(highSigArr6,npArr[-j-bar*5][1])
            highSigArr7 = np.append(highSigArr7,npArr[-j-bar*6][1])
            highSigArr8 = np.append(highSigArr8,npArr[-j-bar*7][1])
            highSigArr9 = np.append(highSigArr9,npArr[-j-bar*8][1])
            highSigArr10 = np.append(highSigArr10,npArr[-j-bar*9][1])
            highSigArr11 = np.append(highSigArr11,npArr[-j-bar*10][1])

        high1 = highSigArr1.max()
        high2 = highSigArr2.max()
        high3 = highSigArr3.max()
        high4 = highSigArr4.max()
        high5 = highSigArr5.max()
        high6 = highSigArr6.max()
        high7 = highSigArr7.max()
        high8 = highSigArr8.max()
        high9 = highSigArr9.max()
        high10 = highSigArr10.max()
        high11 = highSigArr11.max()
        low1 = lowSigArr1.min()
        low2 = lowSigArr2.min()
        low3 = lowSigArr3.min()
        low4 = lowSigArr4.min()
        low5 = lowSigArr5.min()
        low6 = lowSigArr6.min()
        low7 = lowSigArr7.min()
        low8 = lowSigArr8.min()
        low9 = lowSigArr9.min()
        low10 = lowSigArr10.min()
        low11 = lowSigArr11.min()

        if (
            npArr[-bar*10+1][3] < npArr[-bar*11][0] and
            high10 < high11 and
            low10 > low11 and
            high9 < high11 and
            low9 > low11 and
            high8 < high11 and
            low8 > low11 and
            high7 < high11 and
            low7 > low11 and
            high6 < high11 and
            low6 > low11 and
            high5 < high11 and
            low5 > low11 and
            high4 < high11 and
            low4 > low11 and
            high3 < high11 and
            low3 > low11 and
            high2 < high11 and
            low2 > low11 and
            high1 < high11 and
            low1 > low11
        ):
            op = highArrAll.max()
            sl = lowArrAll.min()
            tp = op + (op-sl) * 1.022222222
            message = f"{symbol} 12barPlay reverse add buy op {op} sl {sl} tp {tp}"
            print(message,hour,minute)
        elif (
            npArr[-bar*10+1][3] > npArr[-bar*11][0] and
            high10 < high11 and
            low10 > low11 and
            high9 < high11 and
            low9 > low11 and
            high8 < high11 and
            low8 > low11 and
            high7 < high11 and
            low7 > low11 and
            high6 < high11 and
            low6 > low11 and
            high5 < high11 and
            low5 > low11 and
            high4 < high11 and
            low4 > low11 and
            high3 < high11 and
            low3 > low11 and
            high2 < high11 and
            low2 > low11 and
            high1 < high11 and
            low1 > low11
        ):
            op = lowArrAll.min()
            sl = highArrAll.max()
            tp = op - (sl-op) * 1.022222222
            message = f"{symbol} 12barPlay reverse add sell op {op} sl {sl} tp {tp}"
            print(message,hour,minute)

def init():
    message = "Only Trade Discord Alert!!"
    print(message,hour,minute)

def shutDown():
    message = "SHUT DOWN, GET GREEN GET OUT"
    print(message,hour,minute)
    print(message)

# def openingRangeBko(symbol):
#     global checkPreRange
#     global highRangeAll, lowRangeAll
#     message = "Only Trade PreBreakOut & Discord Alert!!"
#     print(message,hour,minute)
#     print(message)
#     checkPreRange = True
#     if checkPreRange:
#         npArr = GetData(symbol)
#         i = 0
#         highArrAll = np.empty(0)
#         lowArrAll = np.empty(0)
#         for j in range(1, 37+1):
#             highRangeAll = np.append(highArrAll,npArr[i-j][1])
#             lowRangeAll = np.append(lowArrAll,npArr[i-j][2])
#         highRangeAll = 399.01
#         lowRangeAll = 396.94
#         # highRangeAll = 999
#         message = "openingRangeBko +4 point No Trade if last 2 minute HOD/LOD"
#         print(message,hour,minute)
#         print(message)

def main():
    dayLightSaving = True
    symbol = 'CROX'
    # symbolList = ['QQQ','SPY','AAPL']
    # init()
    df = GetDf(symbol)
    
    # while(ib.sleep(1)):
    #     hour = ib.reqCurrentTime().hour
    #     minute = ib.reqCurrentTime().minute
    #     sec = ib.reqCurrentTime().second
    #     if sec == 0:
    #         # if(hour == 13 and minute < 42): continue
    #         # scanner(symbol, hour, minute)
    #         # for symbol in symbolList:
    #         scanner(symbol, hour, minute, npArr)
    #         print('tick')
    #     if dayLightSaving:
    #         if(hour == 14 and minute == 3 and sec == 0):
    #             shutDown()
    #             # return
    #     else:
    #         if(hour == 15 and minute == 3 and sec == 0):
    #             shutDown()
    #             # return
    from datetime import datetime
    startDate = '2022-08-01 22:28:00'
    # endDate = '2022-08-04 05:00:00'
    # startDate = datetime.strptime(startDate, '%Y-%m-%d')
    # df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")
    df = df.loc[df['date'] >= startDate]
    # df = df.loc[df['date'] <= endDate]
    print(len(df))
    df = df.reset_index(drop=True)
    df = df.assign(hour=df['date'].dt.hour)
    df = df.assign(minute=df['date'].dt.minute)
    # print(df)
    hour = 24
    minute = 0
    # hour = 23
    # minute = 16
    while hour <= 4 or hour >= 22:
        if hour == 22 and minute < 32: break
        if hour == 0 and minute == 0: 
            hour = 23
            minute = 60
        if minute > 0:
            minute -= 1
        else:
            hour -= 1
            minute = 59

        idx = df.index[(df.hour == hour) & (df.minute == minute)].tolist()
        if len(idx) > 0:
            idx = idx[-1]
        else:
            continue
        print(idx)
        df = df.head(idx+1)
        df2 = df[['open','high','low','close']]
        npArr = df2.to_numpy()
        scanner(symbol, hour, minute, npArr)


if __name__ == '__main__':
    main()