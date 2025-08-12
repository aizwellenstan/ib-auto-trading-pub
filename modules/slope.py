import numpy as np
import sys
from numba import jit

@jit(nopython=True)
def GetSlopeUpper(npArr, brk = 2, body = False, tch = 4, level = 3, lineLife = 4):
    slopeUpper = 0
    pkArr = [1]
    pk0A = 0
    pk0B = 0
    pk0C = 0
    pk1A = 0
    pk1B = 0
    pk1C = 0
    p = 0
    slope = 0.0
    i = 1

    if(len(npArr) > 90):
        while(i < len(npArr)-30):
            if(
                npArr[-(i+1)][1] >
                npArr[-i][1] and
                npArr[-(i+1)][1] >=
                npArr[-(i+2)][1]
            ):
                pk0C = pk0B
                pk0B = pk0A
                pk0A = i+1
                if (level < 1):
                    pkArr[p] = i+1
                    p+=1
                elif (
                    pk0C > 0 and
                    npArr[-pk0B][1] >
                    npArr[-pk0A][1] and
                    npArr[-pk0B][1] >=
                    npArr[-pk0C][1]
                ):
                    pk1C = pk1B
                    pk1B = pk1A
                    pk1A = pk0B
                    if (level < 2):
                        pkArr[p] = pk0B
                        p+=1;      
                    elif (
                        pk1C > 0 and 
                        npArr[-pk1B][1] >
                        npArr[-pk1A][1] and
                        npArr[-pk1B][1] >=
                        npArr[-pk1C][1]
                    ):
                        pkArr.append(0)
                        pkArr[p] = pk1B
                        p+=1
            i += 1
    x = 0
    j = 0
    l = len(pkArr)
    if (l > 1):
        pkArr.sort(reverse = True)
        i = 0
        while(i < l):
            j = i + 1
            while(j < l):
                t, x = countSlopingCrosses(npArr, pkArr[i], pkArr[j], brk, 0, True, body)
                if ( t > tch and x <= lineLife ):
                    slope = (
                        npArr[-pkArr[i]][1] -
                        npArr[-pkArr[j]][1]
                    ) / (pkArr[i] - pkArr[j])
                    slopeUpper = slope
                j += 1
            i += 1

    return slopeUpper

@jit(nopython=True)
def GetSlopeLower(npArr, brk = 2, body = False, tch = 4, level = 3, lineLife = 4):
    slopeLower = 0
    trArr = [1]
    tr0A = 0
    tr0B = 0
    tr0C = 0
    tr1A = 0
    tr1B = 0
    tr1C = 0
    t = 0
    slope = 0.0
    i = 1

    if(len(npArr) > 90):
        while(i < len(npArr)-30):
            if (
                npArr[-(i+1)][2] <
                npArr[-i][2] and
                npArr[-(i+1)][2] <=
                npArr[-(i+2)][2]
            ):
                tr0C = tr0B
                tr0B = tr0A
                tr0A = i+1
                if (level < 1):
                    trArr[t] = i+1
                    t+=1
                elif (
                    tr0C > 1 and 
                    npArr[-tr0B][2] <
                    npArr[-tr0A][2] and
                    npArr[-tr0B][2] <=
                    npArr[-tr0C][2]
                ):
                    tr1C = tr1B
                    tr1B = tr1A
                    tr1A = tr0B
                    if ( level < 2 ):
                        trArr[t] = tr0B
                        t += 1
                    elif (
                        tr1C > 0 and 
                        npArr[-tr1B][2] <
                        npArr[-tr1A][2] and
                        npArr[-tr1B][2] <
                        npArr[-tr1C][2]
                    ):
                        trArr.append(0)
                        trArr[t] = tr1B
                        t += 1
            i += 1
    x = 0
    j = 0
    l = len(trArr)
    if (l > 1):
        trArr.sort(reverse = True)
        i = 0
        while(i < l):
            j = i + 1
            while(j < l):
                t, x = countSlopingCrosses(npArr, trArr[i], trArr[j], brk, 0, False, body)
                if( t > tch and x <= lineLife ):
                    slope = (
                        npArr[-trArr[i]][2] -
                        npArr[-trArr[j]][2]
                    ) / (trArr[i] - trArr[j])
                    slopeLower = slope
                j += 1
            i += 1

    return slopeLower

@jit(nopython=True)
def GetSlopeUpperNew(npArr, brk = 2, body = False, tch = 4, level = 3, lineLife = 4):
    slopeUpper = 0
    pkArr = [1]
    pk0A = 0
    pk0B = 0
    pk0C = 0
    pk1A = 0
    pk1B = 0
    pk1C = 0
    p = 0
    slope = 0.0
    i = 1

    if(len(npArr) > 2):
        while(i < len(npArr)):
            if(
                npArr[-(i+1)][1] >
                npArr[-i][1] and
                npArr[-(i+1)][1] >=
                npArr[-(i+2)][1]
            ):
                pk0C = pk0B
                pk0B = pk0A
                pk0A = i+1
                if (level < 1):
                    pkArr[p] = i+1
                    p+=1
                elif (
                    pk0C > 0 and
                    npArr[-pk0B][1] >
                    npArr[-pk0A][1] and
                    npArr[-pk0B][1] >=
                    npArr[-pk0C][1]
                ):
                    pk1C = pk1B
                    pk1B = pk1A
                    pk1A = pk0B
                    if (level < 2):
                        pkArr[p] = pk0B
                        p+=1;      
                    elif (
                        pk1C > 0 and 
                        npArr[-pk1B][1] >
                        npArr[-pk1A][1] and
                        npArr[-pk1B][1] >=
                        npArr[-pk1C][1]
                    ):
                        pkArr.append(0)
                        pkArr[p] = pk1B
                        p+=1
            i += 1
    x = 0
    j = 0
    l = len(pkArr)
    if (l > 1):
        pkArr.sort(reverse = True)
        i = 0
        while(i < l):
            j = i + 1
            while(j < l):
                t, x = countSlopingCrosses(npArr, pkArr[i], pkArr[j], brk, 0, True, body)
                if ( t > tch and x <= lineLife ):
                    slope = (
                        npArr[-pkArr[i]][1] -
                        npArr[-pkArr[j]][1]
                    ) / (pkArr[i] - pkArr[j])
                    slopeUpper = slope
                j += 1
            i += 1

    return slopeUpper

@jit(nopython=True)
def GetSlopeLowerNew(npArr, brk = 2, body = False, tch = 4, level = 3, lineLife = 4):
    slopeLower = 0
    trArr = [1]
    tr0A = 0
    tr0B = 0
    tr0C = 0
    tr1A = 0
    tr1B = 0
    tr1C = 0
    t = 0
    slope = 0.0
    i = 1

    if(len(npArr) > 2):
        while(i < len(npArr)):
            if (
                npArr[-(i+1)][2] <
                npArr[-i][2] and
                npArr[-(i+1)][2] <=
                npArr[-(i+2)][2]
            ):
                tr0C = tr0B
                tr0B = tr0A
                tr0A = i+1
                if (level < 1):
                    trArr[t] = i+1
                    t+=1
                elif (
                    tr0C > 1 and 
                    npArr[-tr0B][2] <
                    npArr[-tr0A][2] and
                    npArr[-tr0B][2] <=
                    npArr[-tr0C][2]
                ):
                    tr1C = tr1B
                    tr1B = tr1A
                    tr1A = tr0B
                    if ( level < 2 ):
                        trArr[t] = tr0B
                        t += 1
                    elif (
                        tr1C > 0 and 
                        npArr[-tr1B][2] <
                        npArr[-tr1A][2] and
                        npArr[-tr1B][2] <
                        npArr[-tr1C][2]
                    ):
                        trArr.append(0)
                        trArr[t] = tr1B
                        t += 1
            i += 1
    x = 0
    j = 0
    l = len(trArr)
    if (l > 1):
        trArr.sort(reverse = True)
        i = 0
        while(i < l):
            j = i + 1
            while(j < l):
                t, x = countSlopingCrosses(npArr, trArr[i], trArr[j], brk, 0, False, body)
                if( t > tch and x <= lineLife ):
                    slope = (
                        npArr[-trArr[i]][2] -
                        npArr[-trArr[j]][2]
                    ) / (trArr[i] - trArr[j])
                    slopeLower = slope
                j += 1
            i += 1

    return slopeLower

@jit(nopython=True)
def GetSlope(npArr, brk = 2, body = False, tch = 4, level = 3, lineLife = 4):
    slopeUpper = 0
    slopeLower = 0
    pkArr = [1]
    trArr = [1]
    pk0A = 0
    pk0B = 0
    pk0C = 0
    pk1A = 0
    pk1B = 0
    pk1C = 0
    p = 0
    tr0A = 0
    tr0B = 0
    tr0C = 0
    tr1A = 0
    tr1B = 0
    tr1C = 0
    t = 0
    slope = 0.0
    i = 1

    if(len(npArr) > 90):
        while(i < len(npArr)-30):
            if(
                npArr[-(i+1)][1] >
                npArr[-i][1] and
                npArr[-(i+1)][1] >=
                npArr[-(i+2)][1]
            ):
                pk0C = pk0B
                pk0B = pk0A
                pk0A = i+1
                if (level < 1):
                    pkArr[p] = i+1
                    p+=1
                elif (
                    pk0C > 0 and
                    npArr[-pk0B][1] >
                    npArr[-pk0A][1] and
                    npArr[-pk0B][1] >=
                    npArr[-pk0C][1]
                ):
                    pk1C = pk1B
                    pk1B = pk1A
                    pk1A = pk0B
                    if (level < 2):
                        pkArr[p] = pk0B
                        p+=1;      
                    elif (
                        pk1C > 0 and 
                        npArr[-pk1B][1] >
                        npArr[-pk1A][1] and
                        npArr[-pk1B][1] >=
                        npArr[-pk1C][1]
                    ):
                        pkArr.append(0)
                        pkArr[p] = pk1B
                        p+=1

            if (
                npArr[-(i+1)][2] <
                npArr[-i][2] and
                npArr[-(i+1)][2] <=
                npArr[-(i+2)][2]
            ):
                tr0C = tr0B
                tr0B = tr0A
                tr0A = i+1
                if (level < 1):
                    trArr[t] = i+1
                    t+=1
                elif (
                    tr0C > 1 and 
                    npArr[-tr0B][2] <
                    npArr[-tr0A][2] and
                    npArr[-tr0B][2] <=
                    npArr[-tr0C][2]
                ):
                    tr1C = tr1B
                    tr1B = tr1A
                    tr1A = tr0B
                    if ( level < 2 ):
                        trArr[t] = tr0B
                        t += 1
                    elif (
                        tr1C > 0 and 
                        npArr[-tr1B][2] <
                        npArr[-tr1A][2] and
                        npArr[-tr1B][2] <
                        npArr[-tr1C][2]
                    ):
                        trArr.append(0)
                        trArr[t] = tr1B
                        t += 1
            i += 1
    x = 0
    j = 0
    l = len(pkArr)
    if (l > 1):
        pkArr.sort(reverse = True)
        i = 0
        while(i < l):
            j = i + 1
            while(j < l):
                t, x = countSlopingCrosses(npArr, pkArr[i], pkArr[j], brk, 0, True, body)
                if ( t > tch and x <= lineLife ):
                    slope = (
                        npArr[-pkArr[i]][1] -
                        npArr[-pkArr[j]][1]
                    ) / (pkArr[i] - pkArr[j])
                    slopeUpper = slope
                j += 1
            i += 1

    l = len(trArr)
    if (l > 1):
        trArr.sort(reverse = True)
        i = 0
        while(i < l):
            j = i + 1
            while(j < l):
                t, x = countSlopingCrosses(npArr, trArr[i], trArr[j], brk, 0, False, body)
                if( t > tch and x <= lineLife ):
                    slope = (
                        npArr[-trArr[i]][2] -
                        npArr[-trArr[j]][2]
                    ) / (trArr[i] - trArr[j])
                    slopeLower = slope
                j += 1
            i += 1

    return slopeUpper, slopeLower

@jit(nopython=True)
def countSlopingCrosses(npArr, fromBar, toBar, brk, rng, pk, body):
    t = 0
    x = 0
    lastCross = 0
    flag = False
    slope = 0
    val = 0
    if (pk):
        slope = (
            npArr[-fromBar][1] -
            npArr[-toBar][1]
        )/(fromBar - toBar)
    else:
        slope = (
            npArr[-fromBar][2] -
            npArr[-toBar][2]
        )/(fromBar - toBar)
    i = fromBar
    while (i > 0):
        flag = True
        if(pk):
            val = (
                (slope * (i - fromBar)) + 
                npArr[-fromBar][1]
            )
            if(
                npArr[-i][1] + rng >= val
            ): t += 1
            if(
                body and 
                npArr[-i][0] > val
            ):
                flag = False
                x += 1
            if(
                flag and 
                npArr[-i][3] > val
            ): x += 1
        else:
            val = (
                (slope * (i - fromBar)) + 
                npArr[-fromBar][2]
            )
            if(
                npArr[-i][2] - rng <= val
            ): t += 1
            if(
                body and 
                npArr[-i][0] < val
            ):
                flag = False
                x += 1
            if(
                flag and 
                npArr[-i][3] < val
            ): x += 1
            if(x > brk and brk > 0):
                lastCross = i
                break
        i -= 1
    return(t,lastCross)

# import pandas as pd
# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="365d")

# # df = df[['Open','High','Low','Close']]
# df = df[['Volume','Volume','Volume','Volume']]
# npArr = df.to_numpy()
# slope = GetSlope(npArr)
# print(slope)
# upper = GetSlopeUpper(npArr)
# print(upper)
# lower = GetSlopeLower(npArr)
# print(lower)