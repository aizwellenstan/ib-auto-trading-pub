import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
import talib

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 5
    if tf in ['20 mins']: TP_VAL = 4
    elif tf in ['30 mins']: TP_VAL = 2
    elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[-3:][:,2])
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-3:][:,1])
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp
    

def AdvancedBlock(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    open_prices = npArr[:, 0]
    high_prices = npArr[:, 1]
    low_prices = npArr[:, 2]
    close_prices = npArr[:, 3]

    # Calculate the Advanced Block indicator
    advanced_block = talib.CDLMORNINGDOJISTAR(open_prices, high_prices, low_prices, close_prices)

    if advanced_block[-2] > 0:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    # elif (
    #     npArr[-3][3] < npArr[-3][0] and
    #     npArr[-2][2] > npArr[-3][2] and
    #     npArr[-3][1] - npArr[-2][3] > atr * 3
    # ):
    #     signal = -1
    #     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #     return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0



