import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import numpy as np
from modules.atr import ATR

def ob_coord(use_max, loc, npArr, i):
    ob_btm = float('inf')
    ob_top = float('-inf')
    atrPeriod = 200
    
    # Compute ATR once and reuse it
    atr_values = np.array([ATR(npArr[:j, 1][-atrPeriod:], npArr[:j, 2][-atrPeriod:], npArr[:j, 3][-atrPeriod:]) for j in range(max(loc + 1, 21), i)])
    
    for j, atr in zip(range(max(loc + 1, 21), i), atr_values):
        if (npArr[j, 1] - npArr[j, 2]) < atr * 2:
            if use_max:
                if npArr[j, 1] > ob_top:
                    ob_top = npArr[j, 1]
                    ob_btm = npArr[j, 2] if ob_top == npArr[j, 1] else ob_btm
            else:
                if npArr[j, 2] < ob_btm:
                    ob_btm = npArr[j, 2]
                    ob_top = npArr[j, 1] if ob_btm == npArr[j, 2] else ob_top

    return ob_btm, ob_top

def swings(npArr, length=50):
    os = np.zeros(npArr.shape[0])
    top = np.zeros(npArr.shape[0])
    btm = np.zeros(npArr.shape[0])
    
    bull_ob_btm = bull_ob_top = bear_ob_btm = bear_ob_top = None
    top_cross = btm_cross = False
    top_y = btm_y = None
    top_x = btm_x = 0

    for i in range(length, len(npArr)):
        upper = np.max(npArr[i-length:i, 1])
        lower = np.min(npArr[i-length:i, 2])

        if npArr[i-length-1, 1] > upper:
            os[i-1] = 0
        elif npArr[i-length-1, 2] < lower:
            os[i-1] = 1
        else:
            os[i-1] = os[i-2]

        if os[i-1] == 0 and os[i-2] != 0:
            top[i-1] = npArr[i-length-1, 1]
        if os[i-1] == 1 and os[i-2] != 1:
            btm[i-1] = npArr[i-length-1, 2]

        if top[i-1]:
            top_cross = True
            top_y = top[i-1]
            top_x = i - length - 1
        if btm[i-1]:
            btm_cross = True
            btm_y = btm[i-1]
            btm_x = i - length - 1
        
        if top_cross and npArr[i, 3] > top_y:
            bull_ob_btm, bull_ob_top = ob_coord(False, top_x, npArr, i)
            top_cross = False
        
        if btm_cross and npArr[i, 3] < btm_y:
            bear_ob_btm, bear_ob_top = ob_coord(True, btm_x, npArr, i)
            btm_cross = False

    return bull_ob_btm, bull_ob_top, bear_ob_btm, bear_ob_top


import yfinance as yf

# Fetch historical data
ticker = "VZ"
data = yf.download(ticker, start='2020-01-01', end='2024-11-14', interval='1d')
data["Date"] = data.index
data[["Open", "High", "Low", "Close"]] = data[["Open", "High", "Low", "Close"]].round(2)
npArr = data[["Open", "High", "Low", "Close", "Date"]].to_numpy()

bull_ob_btm, bull_ob_top, bear_ob_btm, bear_ob_top = swings(npArr)
print(bull_ob_btm, bull_ob_top, bear_ob_btm, bear_ob_top)
